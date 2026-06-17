import { useMany } from "@refinedev/core";
import {
  Create,
  DeleteButton,
  Edit,
  EditButton,
  List,
  useForm,
  useSelect,
  useTable,
} from "@refinedev/antd";
import {
  Avatar,
  Button,
  Form,
  Image,
  Input,
  Select,
  Space,
  Switch,
  Table,
  Tag,
  Typography,
  Upload,
  message,
} from "antd";
import {
  DeleteOutlined,
  ShoppingOutlined,
  StarOutlined,
  UploadOutlined,
} from "@ant-design/icons";
import { useEffect, useState } from "react";

import { MoneyInput, NumberInput } from "../components/inputs";
import { money } from "../lib/format";
import { uploadImage } from "../providers/apiClient";

const { Text } = Typography;

interface IProduct {
  id: number;
  name: string;
  category_id: number | null;
  price: number;
  cost_price: number;
  stock_qty: number;
  is_active: boolean;
  description?: string;
  image_url?: string;
  gallery?: string[];
}

interface ICategoryRef {
  id: number;
  name: string;
}

export const ProductList = () => {
  const { tableProps } = useTable<IProduct>({ syncWithLocation: true });

  // Kategoriya nomlarini ID o'rniga ko'rsatish uchun
  const rows = (tableProps.dataSource ?? []) as IProduct[];
  const categoryIds = [
    ...new Set(rows.map((p) => p.category_id).filter((v): v is number => v != null)),
  ];
  const { data: categoriesData } = useMany<ICategoryRef>({
    resource: "categories",
    ids: categoryIds,
    queryOptions: { enabled: categoryIds.length > 0 },
  });
  const categoryName = (id: number | null) =>
    id == null ? null : categoriesData?.data.find((c) => c.id === id)?.name;

  return (
    <List title="Mahsulotlar">
      <Image.PreviewGroup>
        <Table {...tableProps} rowKey="id">
          <Table.Column
            title=""
            dataIndex="image_url"
            width={64}
            render={(url?: string) =>
              url ? (
                <Image
                  src={url}
                  width={44}
                  height={44}
                  style={{ objectFit: "cover", borderRadius: 6 }}
                />
              ) : (
                <Avatar shape="square" size={44} icon={<ShoppingOutlined />} />
              )
            }
          />
          <Table.Column
            dataIndex="name"
            title="Nomi"
            render={(name: string, r: IProduct) => (
              <Space direction="vertical" size={0}>
                <span>{name}</span>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {categoryName(r.category_id) ?? "Kategoriyasiz"}
                </Text>
              </Space>
            )}
          />
          <Table.Column
            dataIndex="price"
            title="Narx"
            align="right"
            render={(v) => money(v)}
          />
          <Table.Column
            dataIndex="cost_price"
            title="Tannarx"
            align="right"
            render={(v) => money(v)}
          />
          <Table.Column
            dataIndex="stock_qty"
            title="Qoldiq"
            align="center"
            render={(v: number) => (
              <Tag color={v > 0 ? (v < 5 ? "orange" : "green") : "red"}>{v}</Tag>
            )}
          />
          <Table.Column
            dataIndex="is_active"
            title="Faol"
            align="center"
            render={(v: boolean) => (
              <Tag color={v ? "green" : "default"}>{v ? "Ha" : "Yo'q"}</Tag>
            )}
          />
          <Table.Column<IProduct>
            title="Amallar"
            render={(_, record) => (
              <Space>
                <EditButton hideText size="small" recordItemId={record.id} />
                <DeleteButton hideText size="small" recordItemId={record.id} />
              </Space>
            )}
          />
        </Table>
      </Image.PreviewGroup>
    </List>
  );
};

// gallery (massiv) yashirin form maydoni uchun — ko'rinmas controlled control.
const NoopControl = (_: { value?: string[]; onChange?: (v: string[]) => void }) => null;

const ImageField = () => {
  const form = Form.useFormInstance();
  const gallery: string[] = Form.useWatch("gallery", form) ?? [];
  const imageUrl: string | undefined = Form.useWatch("image_url", form);
  const [loading, setLoading] = useState(false);

  // Eski mahsulot (gallery bo'sh, lekin image_url bor) — bir marta gallery'ga ko'chiramiz
  useEffect(() => {
    const current = form.getFieldValue("gallery") as string[] | undefined;
    if ((!current || current.length === 0) && imageUrl) {
      form.setFieldValue("gallery", [imageUrl]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [imageUrl]);

  const setGallery = (next: string[]) => {
    form.setFieldValue("gallery", next);
    form.setFieldValue("image_url", next[0]); // muqova = birinchi rasm (ro'yxat thumbnaili)
  };

  const customRequest = async (opts: any) => {
    setLoading(true);
    try {
      const { url } = await uploadImage(opts.file as File);
      const current = (form.getFieldValue("gallery") as string[]) ?? [];
      setGallery([...current, url]);
      message.success("Rasm yuklandi");
      opts.onSuccess?.({}, opts.file);
    } catch (e: any) {
      message.error(e?.message ?? "Yuklab bo'lmadi");
      opts.onError?.(e);
    } finally {
      setLoading(false);
    }
  };

  const remove = (url: string) =>
    setGallery(((form.getFieldValue("gallery") as string[]) ?? []).filter((u) => u !== url));

  const makeCover = (url: string) => {
    const rest = ((form.getFieldValue("gallery") as string[]) ?? []).filter((u) => u !== url);
    setGallery([url, ...rest]);
  };

  return (
    <Form.Item label={`Rasmlar${gallery.length ? ` (${gallery.length})` : ""}`}>
      {gallery.length > 0 && (
        <Image.PreviewGroup>
          <Space wrap style={{ marginBottom: 12 }}>
            {gallery.map((url, i) => (
              <Space key={url} direction="vertical" size={4} style={{ width: 96 }}>
                <div style={{ position: "relative" }}>
                  <Image
                    src={url}
                    width={96}
                    height={96}
                    style={{ objectFit: "cover", borderRadius: 8 }}
                  />
                  {i === 0 && (
                    <Tag
                      color="gold"
                      style={{ position: "absolute", top: 4, left: 4, margin: 0 }}
                    >
                      Muqova
                    </Tag>
                  )}
                </div>
                <Space size={4}>
                  {i !== 0 && (
                    <Button
                      size="small"
                      icon={<StarOutlined />}
                      title="Muqova qilish"
                      onClick={() => makeCover(url)}
                    />
                  )}
                  <Button
                    size="small"
                    danger
                    icon={<DeleteOutlined />}
                    title="O'chirish"
                    onClick={() => remove(url)}
                  />
                </Space>
              </Space>
            ))}
          </Space>
        </Image.PreviewGroup>
      )}
      <Upload showUploadList={false} accept="image/*" multiple customRequest={customRequest}>
        <Button icon={<UploadOutlined />} loading={loading}>
          Rasm qo'shish
        </Button>
      </Upload>
      <Text type="secondary" style={{ display: "block", marginTop: 6, fontSize: 12 }}>
        Bir nechta rasm tanlash mumkin. Birinchisi — muqova. Botda albom max 10 ta rasm.
      </Text>
      {/* Qiymatlar yashirin maydonlarda saqlanadi va yuboriladi */}
      <Form.Item name="gallery" hidden>
        <NoopControl />
      </Form.Item>
      <Form.Item name="image_url" hidden>
        <Input />
      </Form.Item>
    </Form.Item>
  );
};

const ProductForm = () => {
  const { selectProps: categorySelect } = useSelect({
    resource: "categories",
    optionLabel: "name",
    optionValue: "id",
  });

  return (
    <>
      <Form.Item
        label="Nomi"
        name="name"
        rules={[{ required: true, message: "Nom kiriting" }]}
      >
        <Input />
      </Form.Item>
      <Form.Item label="Kategoriya" name="category_id">
        <Select {...categorySelect} allowClear placeholder="Tanlang" />
      </Form.Item>
      <Form.Item label="Tavsif" name="description">
        <Input.TextArea rows={3} />
      </Form.Item>
      <ImageField />
      <Form.Item
        label="Narx"
        name="price"
        rules={[{ required: true, message: "Narx kiriting" }]}
      >
        <MoneyInput />
      </Form.Item>
      <Form.Item label="Tannarx" name="cost_price">
        <MoneyInput />
      </Form.Item>
      <Form.Item label="Qoldiq" name="stock_qty">
        <NumberInput addonAfter="dona" />
      </Form.Item>
      <Form.Item label="Faol" name="is_active" valuePropName="checked" initialValue={true}>
        <Switch />
      </Form.Item>
    </>
  );
};

export const ProductCreate = () => {
  const { formProps, saveButtonProps } = useForm({ redirect: "list" });
  return (
    <Create title="Yangi mahsulot" saveButtonProps={saveButtonProps}>
      <Form {...formProps} layout="vertical">
        <ProductForm />
      </Form>
    </Create>
  );
};

export const ProductEdit = () => {
  const { formProps, saveButtonProps } = useForm({ redirect: "list" });
  return (
    <Edit title="Mahsulotni tahrirlash" saveButtonProps={saveButtonProps}>
      <Form {...formProps} layout="vertical">
        <ProductForm />
      </Form>
    </Edit>
  );
};
