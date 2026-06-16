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

interface IPromo {
  id: number;
  code: string;
  type: string;
  value: number;
  used_count: number;
  usage_limit: number | null;
  scope: string;
  target_id: number | null;
  is_active: boolean;
}

interface INamed {
  id: number;
  name: string;
}

const TYPE_OPTIONS = [
  { label: "Foiz (%)", value: "percent" },
  { label: "Belgilangan summa", value: "fixed" },
  { label: "Bepul yetkazib berish", value: "free_delivery" },
];
const SCOPE_OPTIONS = [
  { label: "Hammasiga", value: "all" },
  { label: "Kategoriya", value: "category" },
  { label: "Mahsulot", value: "product" },
];

export const PromoList = () => {
  const { tableProps } = useTable<IPromo>({ syncWithLocation: true });
  const rows = (tableProps.dataSource ?? []) as IPromo[];

  // Qamrov maqsadi (mahsulot/kategoriya) nomlarini ID o'rniga ko'rsatish
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
  const scopeLabel = (scope: string, targetId: number | null) => {
    const label = SCOPE_LABELS[scope] ?? scope;
    if (scope === "all" || targetId == null) return label;
    const pool = scope === "product" ? products?.data : categories?.data;
    const name = pool?.find((x) => x.id === targetId)?.name;
    return name ? `${label}: ${name}` : `${label} #${targetId}`;
  };

  return (
    <List title="Promokodlar">
      <Table {...tableProps} rowKey="id">
        <Table.Column dataIndex="id" title="#" width={50} />
        <Table.Column
          dataIndex="code"
          title="Kod"
          render={(c: string) => <Tag color="magenta">{c}</Tag>}
        />
        <Table.Column
          dataIndex="type"
          title="Qiymat"
          render={(t: string, r: IPromo) =>
            t === "percent" ? `${r.value}%` : t === "fixed" ? money(r.value) : "Bepul yetkazib"
          }
        />
        <Table.Column<IPromo>
          title="Qamrov"
          render={(_, r) => scopeLabel(r.scope, r.target_id)}
        />
        <Table.Column
          title="Ishlatilgan"
          render={(_, r: IPromo) =>
            `${r.used_count}${r.usage_limit ? ` / ${r.usage_limit}` : ""}`
          }
        />
        <Table.Column
          dataIndex="is_active"
          title="Faol"
          render={(v: boolean) => (
            <Tag color={v ? "green" : "default"}>{v ? "Ha" : "Yo'q"}</Tag>
          )}
        />
        <Table.Column<IPromo>
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

const PromoForm = () => (
  <>
    <Form.Item label="Kod" name="code" rules={[{ required: true }]}>
      <Input placeholder="BAHOR2026" />
    </Form.Item>
    <Form.Item label="Turi" name="type" initialValue="percent">
      <Select options={TYPE_OPTIONS} />
    </Form.Item>
    <Form.Item label="Qiymat" name="value" help="Foiz uchun 1–100, summa uchun so'm. Bepul yetkazib uchun 0.">
      <InputNumber style={{ width: "100%" }} min={0} />
    </Form.Item>
    <Form.Item label="Minimal buyurtma summasi" name="min_order_amount" initialValue={0}>
      <InputNumber style={{ width: "100%" }} min={0} step={1000} />
    </Form.Item>
    <Form.Item label="Maksimal chegirma (foiz uchun)" name="max_discount">
      <InputNumber style={{ width: "100%" }} min={0} step={1000} />
    </Form.Item>
    <Form.Item label="Umumiy limit" name="usage_limit" help="Bo'sh = cheksiz">
      <InputNumber style={{ width: "100%" }} min={1} />
    </Form.Item>
    <Form.Item label="Bir mijozga limit" name="per_user_limit" help="Bo'sh = cheksiz">
      <InputNumber style={{ width: "100%" }} min={1} />
    </Form.Item>
    <Form.Item label="Faqat birinchi buyurtma" name="first_order_only" valuePropName="checked" initialValue={false}>
      <Switch />
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

export const PromoCreate = () => {
  const { formProps, saveButtonProps } = useForm({ redirect: "list" });
  return (
    <Create title="Yangi promokod" saveButtonProps={saveButtonProps}>
      <Form {...formProps} layout="vertical">
        <PromoForm />
      </Form>
    </Create>
  );
};

export const PromoEdit = () => {
  const { formProps, saveButtonProps } = useForm({ redirect: "list" });
  return (
    <Edit title="Promokodni tahrirlash" saveButtonProps={saveButtonProps}>
      <Form {...formProps} layout="vertical">
        <PromoForm />
      </Form>
    </Edit>
  );
};
