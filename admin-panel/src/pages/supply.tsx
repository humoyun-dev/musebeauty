import { Create, List, useForm, useSelect, useTable } from "@refinedev/antd";
import { MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";
import {
  Button,
  Form,
  Input,
  InputNumber,
  Select,
  Space,
  Table,
  Typography,
} from "antd";

import { money } from "../lib/format";

const { Text } = Typography;

interface ISupplyBatch {
  id: number;
  supplier?: string;
  total_cost: number;
  note?: string;
}

export const SupplyList = () => {
  const { tableProps } = useTable<ISupplyBatch>({ syncWithLocation: true });
  return (
    <List title="Ta'minot partiyalari">
      <Text type="secondary">
        Partiya kiritilganda mahsulot qoldig'i oshadi va o'rtacha tannarx qayta
        hisoblanadi.
      </Text>
      <Table {...tableProps} rowKey="id" style={{ marginTop: 16 }}>
        <Table.Column dataIndex="id" title="#" width={60} />
        <Table.Column dataIndex="supplier" title="Yetkazib beruvchi" />
        <Table.Column
          dataIndex="total_cost"
          title="Umumiy summa"
          render={(v) => money(v)}
        />
        <Table.Column dataIndex="note" title="Izoh" />
      </Table>
    </List>
  );
};

export const SupplyCreate = () => {
  const { formProps, saveButtonProps } = useForm({ redirect: "list" });
  const { selectProps: productSelect } = useSelect({
    resource: "products",
    optionLabel: "name",
    optionValue: "id",
  });

  return (
    <Create title="Yangi partiya kiritish" saveButtonProps={saveButtonProps}>
      <Form {...formProps} layout="vertical">
        <Form.Item label="Yetkazib beruvchi" name="supplier">
          <Input placeholder="Korea Cosmetics Co." />
        </Form.Item>
        <Form.Item label="Izoh" name="note">
          <Input.TextArea rows={2} />
        </Form.Item>

        <Text strong>Mahsulotlar</Text>
        <Form.List name="items" initialValue={[{}]}>
          {(fields, { add, remove }) => (
            <>
              {fields.map(({ key, name, ...rest }) => (
                <Space key={key} align="baseline" style={{ display: "flex", marginTop: 8 }}>
                  <Form.Item
                    {...rest}
                    name={[name, "product_id"]}
                    rules={[{ required: true, message: "Mahsulot" }]}
                    style={{ minWidth: 220 }}
                  >
                    <Select {...productSelect} placeholder="Mahsulot" />
                  </Form.Item>
                  <Form.Item
                    {...rest}
                    name={[name, "qty"]}
                    rules={[{ required: true, message: "Miqdor" }]}
                  >
                    <InputNumber min={1} placeholder="Miqdor" />
                  </Form.Item>
                  <Form.Item
                    {...rest}
                    name={[name, "unit_cost"]}
                    rules={[{ required: true, message: "Dona tannarx" }]}
                  >
                    <InputNumber min={0} step={1000} placeholder="Dona tannarx" />
                  </Form.Item>
                  {fields.length > 1 && (
                    <MinusCircleOutlined onClick={() => remove(name)} />
                  )}
                </Space>
              ))}
              <Form.Item style={{ marginTop: 8 }}>
                <Button type="dashed" onClick={() => add()} icon={<PlusOutlined />} block>
                  Mahsulot qo'shish
                </Button>
              </Form.Item>
            </>
          )}
        </Form.List>
      </Form>
    </Create>
  );
};
