import {
  Create,
  Edit,
  EditButton,
  List,
  useForm,
  useTable,
} from "@refinedev/antd";
import { Form, Input, Space, Switch, Table, Tag } from "antd";

interface ICategory {
  id: number;
  name: string;
  slug: string;
  is_active: boolean;
}

export const CategoryList = () => {
  const { tableProps } = useTable<ICategory>({ syncWithLocation: true });
  return (
    <List title="Kategoriyalar">
      <Table {...tableProps} rowKey="id">
        <Table.Column dataIndex="id" title="ID" width={60} />
        <Table.Column dataIndex="name" title="Nomi" />
        <Table.Column dataIndex="slug" title="Slug" />
        <Table.Column
          dataIndex="is_active"
          title="Faol"
          render={(v: boolean) => (
            <Tag color={v ? "green" : "default"}>{v ? "Ha" : "Yo'q"}</Tag>
          )}
        />
        <Table.Column<ICategory>
          title="Amallar"
          render={(_, record) => (
            <Space>
              <EditButton hideText size="small" recordItemId={record.id} />
            </Space>
          )}
        />
      </Table>
    </List>
  );
};

const CategoryForm = () => (
  <>
    <Form.Item
      label="Nomi"
      name="name"
      rules={[{ required: true, message: "Nom kiriting" }]}
    >
      <Input />
    </Form.Item>
    <Form.Item
      label="Slug"
      name="slug"
      help="Bo'sh qoldirsangiz nomdan avtomatik hosil bo'ladi"
    >
      <Input placeholder="yuz-parvarishi" />
    </Form.Item>
    <Form.Item label="Faol" name="is_active" valuePropName="checked" initialValue={true}>
      <Switch />
    </Form.Item>
  </>
);

export const CategoryCreate = () => {
  const { formProps, saveButtonProps } = useForm({ redirect: "list" });
  return (
    <Create title="Yangi kategoriya" saveButtonProps={saveButtonProps}>
      <Form {...formProps} layout="vertical">
        <CategoryForm />
      </Form>
    </Create>
  );
};

export const CategoryEdit = () => {
  const { formProps, saveButtonProps } = useForm({ redirect: "list" });
  return (
    <Edit title="Kategoriyani tahrirlash" saveButtonProps={saveButtonProps}>
      <Form {...formProps} layout="vertical">
        <CategoryForm />
      </Form>
    </Edit>
  );
};
