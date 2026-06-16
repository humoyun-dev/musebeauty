import { useMany } from "@refinedev/core";
import {
  Create,
  DeleteButton,
  Edit,
  EditButton,
  List,
  useForm,
  useTable,
} from "@refinedev/antd";
import { Form, Input, InputNumber, Select, Space, Switch, Table, Tag } from "antd";

import { money, SCOPE_LABELS } from "../lib/format";

interface IDiscount {
  id: number;
  name: string;
  type: string;
  value: number;
  scope: string;
  target_id: number | null;
  is_active: boolean;
}

interface INamed {
  id: number;
  name: string;
}

// Qamrov + maqsad nomini birga ko'rsatadi (ID o'rniga nom)
const useScopeLabeller = (rows: IDiscount[]) => {
  const productIds = [
    ...new Set(
      rows
        .filter((r) => r.scope === "product" && r.target_id != null)
        .map((r) => r.target_id as number),
    ),
  ];
  const categoryIds = [
    ...new Set(
      rows
        .filter((r) => r.scope === "category" && r.target_id != null)
        .map((r) => r.target_id as number),
    ),
  ];
  const { data: products } = useMany<INamed>({
    resource: "products",
    ids: productIds,
    queryOptions: { enabled: productIds.length > 0 },
  });
  const { data: categories } = useMany<INamed>({
    resource: "categories",
    ids: categoryIds,
    queryOptions: { enabled: categoryIds.length > 0 },
  });

  return (scope: string, targetId: number | null) => {
    const label = SCOPE_LABELS[scope] ?? scope;
    if (scope === "all" || targetId == null) return label;
    const pool = scope === "product" ? products?.data : categories?.data;
    const name = pool?.find((x) => x.id === targetId)?.name;
    return name ? `${label}: ${name}` : `${label} #${targetId}`;
  };
};

const TYPE_OPTIONS = [
  { label: "Foiz (%)", value: "percent" },
  { label: "Belgilangan summa", value: "fixed" },
];
const SCOPE_OPTIONS = [
  { label: "Hammasiga", value: "all" },
  { label: "Kategoriya", value: "category" },
  { label: "Mahsulot", value: "product" },
];

export const DiscountList = () => {
  const { tableProps } = useTable<IDiscount>({ syncWithLocation: true });
  const rows = (tableProps.dataSource ?? []) as IDiscount[];
  const scopeLabel = useScopeLabeller(rows);

  return (
    <List title="Chegirmalar (kodsiz, avtomatik)">
      <Table {...tableProps} rowKey="id">
        <Table.Column dataIndex="id" title="#" width={50} />
        <Table.Column dataIndex="name" title="Nomi" />
        <Table.Column
          dataIndex="type"
          title="Qiymat"
          render={(t: string, r: IDiscount) =>
            t === "percent" ? `${r.value}%` : money(r.value)
          }
        />
        <Table.Column<IDiscount>
          title="Qamrov"
          render={(_, r) => scopeLabel(r.scope, r.target_id)}
        />
        <Table.Column
          dataIndex="is_active"
          title="Faol"
          render={(v: boolean) => (
            <Tag color={v ? "green" : "default"}>{v ? "Ha" : "Yo'q"}</Tag>
          )}
        />
        <Table.Column<IDiscount>
          title="Amallar"
          render={(_, r) => (
            <Space>
              <EditButton hideText size="small" recordItemId={r.id} />
              <DeleteButton hideText size="small" recordItemId={r.id} />
            </Space>
          )}
        />
      </Table>
    </List>
  );
};

const DiscountForm = () => (
  <>
    <Form.Item label="Nomi" name="name" rules={[{ required: true }]}>
      <Input placeholder="Bahor aksiyasi" />
    </Form.Item>
    <Form.Item label="Turi" name="type" initialValue="percent">
      <Select options={TYPE_OPTIONS} />
    </Form.Item>
    <Form.Item label="Qiymat" name="value" rules={[{ required: true }]} help="Foiz uchun 1–100, summa uchun so'm">
      <InputNumber style={{ width: "100%" }} min={0} />
    </Form.Item>
    <Form.Item label="Qamrov" name="scope" initialValue="all">
      <Select options={SCOPE_OPTIONS} />
    </Form.Item>
    <Form.Item label="Maqsad ID" name="target_id" help="Qamrov=kategoriya/mahsulot bo'lsa: tegishli ID">
      <InputNumber style={{ width: "100%" }} min={1} />
    </Form.Item>
    <Form.Item label="Faol" name="is_active" valuePropName="checked" initialValue={true}>
      <Switch />
    </Form.Item>
  </>
);

export const DiscountCreate = () => {
  const { formProps, saveButtonProps } = useForm({ redirect: "list" });
  return (
    <Create title="Yangi chegirma" saveButtonProps={saveButtonProps}>
      <Form {...formProps} layout="vertical">
        <DiscountForm />
      </Form>
    </Create>
  );
};

export const DiscountEdit = () => {
  const { formProps, saveButtonProps } = useForm({ redirect: "list" });
  return (
    <Edit title="Chegirmani tahrirlash" saveButtonProps={saveButtonProps}>
      <Form {...formProps} layout="vertical">
        <DiscountForm />
      </Form>
    </Edit>
  );
};
