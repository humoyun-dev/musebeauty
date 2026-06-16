import { useCustomMutation, useMany, useOne, useShow } from "@refinedev/core";
import { List, Show, ShowButton, useTable } from "@refinedev/antd";
import {
  Avatar,
  Button,
  Card,
  Col,
  Descriptions,
  Image,
  Row,
  Space,
  Table,
  Tag,
  Typography,
  message,
} from "antd";
import {
  EnvironmentOutlined,
  ShoppingOutlined,
  UserOutlined,
} from "@ant-design/icons";

import {
  dateTime,
  money,
  NEXT_STATUSES,
  ORDER_STATUS,
  PAYMENT_STATUS,
} from "../lib/format";

const { Text } = Typography;

interface IOrderItem {
  product_id: number;
  qty: number;
  unit_price: number;
  cost_price?: number;
}
interface IOrder {
  id: number;
  customer_id: number;
  status: string;
  payment_status: string;
  address?: string;
  phone?: string;
  latitude?: number | null;
  longitude?: number | null;
  subtotal: number;
  discount_amount: number;
  delivery_fee: number;
  total: number;
  created_at: string;
  items: IOrderItem[];
}

// Buyurtma qatorlarini boyitish uchun yengil ko'rinishlar
interface IProductRef {
  id: number;
  name: string;
  image_url?: string;
}
interface ICustomerRef {
  id: number;
  name?: string;
  phone?: string;
  telegram_id?: number;
}

const statusTag = (s: string) => {
  const cfg = ORDER_STATUS[s] ?? { label: s, color: "default" };
  return <Tag color={cfg.color}>{cfg.label}</Tag>;
};

const paymentTag = (s: string) => {
  const cfg = PAYMENT_STATUS[s] ?? { label: s, color: "default" };
  return <Tag color={cfg.color}>{cfg.label}</Tag>;
};

const itemsCount = (items?: IOrderItem[]) =>
  (items ?? []).reduce((sum, i) => sum + i.qty, 0);

export const OrderList = () => {
  const { tableProps } = useTable<IOrder>({
    syncWithLocation: true,
    sorters: { initial: [{ field: "id", order: "desc" }] },
  });

  // Joriy sahifadagi buyurtmalar uchun mijoz ismlarini bitta so'rovda olamiz
  const rows = (tableProps.dataSource ?? []) as IOrder[];
  const customerIds = [...new Set(rows.map((o) => o.customer_id).filter(Boolean))];
  const { data: customersData } = useMany<ICustomerRef>({
    resource: "customers",
    ids: customerIds,
    queryOptions: { enabled: customerIds.length > 0 },
  });
  const customerName = (id: number) =>
    customersData?.data.find((c) => c.id === id)?.name;

  return (
    <List title="Buyurtmalar">
      <Table {...tableProps} rowKey="id">
        <Table.Column
          dataIndex="id"
          title="#"
          width={64}
          render={(v: number) => <Text strong>#{v}</Text>}
        />
        <Table.Column<IOrder>
          title="Mijoz"
          render={(_, r) => (
            <Space direction="vertical" size={0}>
              <span>{customerName(r.customer_id) ?? `Mijoz #${r.customer_id}`}</span>
              {r.phone && (
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {r.phone}
                </Text>
              )}
            </Space>
          )}
        />
        <Table.Column<IOrder>
          title="Mahsulotlar"
          width={120}
          render={(_, r) => `${itemsCount(r.items)} dona`}
        />
        <Table.Column
          dataIndex="total"
          title="Summa"
          align="right"
          render={(v) => <Text strong>{money(v)}</Text>}
        />
        <Table.Column dataIndex="status" title="Holat" render={statusTag} />
        <Table.Column
          dataIndex="payment_status"
          title="To'lov"
          render={paymentTag}
        />
        <Table.Column
          dataIndex="created_at"
          title="Sana"
          render={(v: string) => dateTime(v)}
        />
        <Table.Column<IOrder>
          title=""
          width={56}
          render={(_, record) => (
            <ShowButton hideText size="small" recordItemId={record.id} />
          )}
        />
      </Table>
    </List>
  );
};

export const OrderShow = () => {
  const { queryResult } = useShow<IOrder>();
  const { data, isLoading, refetch } = queryResult;
  const order = data?.data;

  // Mahsulot nomlari/rasmlari — qatorlardagi product_id'lar bo'yicha
  const productIds = [...new Set((order?.items ?? []).map((i) => i.product_id))];
  const { data: productsData } = useMany<IProductRef>({
    resource: "products",
    ids: productIds,
    queryOptions: { enabled: productIds.length > 0 },
  });
  const productMap = new Map(
    (productsData?.data ?? []).map((p) => [p.id, p]),
  );

  // Mijoz ma'lumotlari
  const { data: customerData } = useOne<ICustomerRef>({
    resource: "customers",
    id: order?.customer_id ?? 0,
    queryOptions: { enabled: !!order?.customer_id },
  });
  const customer = customerData?.data;

  const { mutate, isLoading: isMutating } = useCustomMutation();

  const changeStatus = (status: string) => {
    if (!order) return;
    mutate(
      {
        url: `/orders/${order.id}/status`,
        method: "patch",
        values: { status },
      },
      {
        onSuccess: () => {
          message.success("Holat yangilandi");
          refetch();
        },
        onError: (e: any) => message.error(e?.message ?? "Xatolik"),
      },
    );
  };

  const nextStatuses = order ? NEXT_STATUSES[order.status] ?? [] : [];
  const hasCoords =
    order?.latitude != null && order?.longitude != null;

  return (
    <Show
      isLoading={isLoading}
      title={order ? `Buyurtma #${order.id}` : "Buyurtma"}
    >
      {order && (
        <Row gutter={[16, 16]}>
          {/* Chap ustun: tarkib + holat tugmalari */}
          <Col xs={24} lg={15}>
            <Card size="small" title="Buyurtma tarkibi">
              <Image.PreviewGroup>
                <Table
                  dataSource={order.items}
                  rowKey={(r) => `${r.product_id}`}
                  pagination={false}
                  size="small"
                  summary={() => (
                    <Table.Summary>
                      <Table.Summary.Row>
                        <Table.Summary.Cell index={0} colSpan={3} align="right">
                          <Text type="secondary">Mahsulotlar</Text>
                        </Table.Summary.Cell>
                        <Table.Summary.Cell index={3} align="right">
                          {money(order.subtotal)}
                        </Table.Summary.Cell>
                      </Table.Summary.Row>
                      {Number(order.discount_amount) > 0 && (
                        <Table.Summary.Row>
                          <Table.Summary.Cell index={0} colSpan={3} align="right">
                            <Text type="secondary">Chegirma</Text>
                          </Table.Summary.Cell>
                          <Table.Summary.Cell index={3} align="right">
                            <Text type="success">
                              − {money(order.discount_amount)}
                            </Text>
                          </Table.Summary.Cell>
                        </Table.Summary.Row>
                      )}
                      <Table.Summary.Row>
                        <Table.Summary.Cell index={0} colSpan={3} align="right">
                          <Text type="secondary">Yetkazib berish</Text>
                        </Table.Summary.Cell>
                        <Table.Summary.Cell index={3} align="right">
                          {money(order.delivery_fee)}
                        </Table.Summary.Cell>
                      </Table.Summary.Row>
                      <Table.Summary.Row>
                        <Table.Summary.Cell index={0} colSpan={3} align="right">
                          <Text strong>Jami</Text>
                        </Table.Summary.Cell>
                        <Table.Summary.Cell index={3} align="right">
                          <Text strong style={{ fontSize: 16 }}>
                            {money(order.total)}
                          </Text>
                        </Table.Summary.Cell>
                      </Table.Summary.Row>
                    </Table.Summary>
                  )}
                >
                  <Table.Column<IOrderItem>
                    title="Mahsulot"
                    render={(_, r) => {
                      const p = productMap.get(r.product_id);
                      return (
                        <Space>
                          {p?.image_url ? (
                            <Image
                              src={p.image_url}
                              width={40}
                              height={40}
                              style={{ objectFit: "cover", borderRadius: 6 }}
                            />
                          ) : (
                            <Avatar
                              shape="square"
                              size={40}
                              icon={<ShoppingOutlined />}
                            />
                          )}
                          <Space direction="vertical" size={0}>
                            <span>{p?.name ?? `Mahsulot #${r.product_id}`}</span>
                            <Text type="secondary" style={{ fontSize: 12 }}>
                              #{r.product_id}
                            </Text>
                          </Space>
                        </Space>
                      );
                    }}
                  />
                  <Table.Column
                    dataIndex="qty"
                    title="Miqdor"
                    align="center"
                    width={90}
                  />
                  <Table.Column
                    dataIndex="unit_price"
                    title="Narx"
                    align="right"
                    width={140}
                    render={(v) => money(v)}
                  />
                  <Table.Column
                    title="Jami"
                    align="right"
                    width={140}
                    render={(_, r: IOrderItem) => money(r.unit_price * r.qty)}
                  />
                </Table>
              </Image.PreviewGroup>
            </Card>

            {nextStatuses.length > 0 && (
              <Card
                size="small"
                title="Holatni o'zgartirish"
                style={{ marginTop: 16 }}
              >
                <Space wrap>
                  {nextStatuses.map((s) => (
                    <Button
                      key={s}
                      loading={isMutating}
                      danger={s === "bekor_qilindi" || s === "qaytarildi"}
                      type={s === "bekor_qilindi" ? "default" : "primary"}
                      onClick={() => changeStatus(s)}
                    >
                      {(ORDER_STATUS[s] ?? { label: s }).label}
                    </Button>
                  ))}
                </Space>
              </Card>
            )}
          </Col>

          {/* O'ng ustun: holat, mijoz, yetkazib berish */}
          <Col xs={24} lg={9}>
            <Card size="small">
              <Descriptions column={1} size="small" colon={false}>
                <Descriptions.Item label="Holat">
                  {statusTag(order.status)}
                </Descriptions.Item>
                <Descriptions.Item label="To'lov">
                  {paymentTag(order.payment_status)}
                </Descriptions.Item>
                <Descriptions.Item label="Sana">
                  {dateTime(order.created_at)}
                </Descriptions.Item>
              </Descriptions>
            </Card>

            <Card
              size="small"
              title={
                <Space>
                  <UserOutlined />
                  Mijoz
                </Space>
              }
              style={{ marginTop: 16 }}
            >
              <Descriptions column={1} size="small">
                <Descriptions.Item label="Ism">
                  {customer?.name ?? "—"}
                </Descriptions.Item>
                <Descriptions.Item label="Telefon">
                  {order.phone ? (
                    <a href={`tel:${order.phone}`}>{order.phone}</a>
                  ) : (
                    "—"
                  )}
                </Descriptions.Item>
                {customer?.telegram_id != null && (
                  <Descriptions.Item label="Telegram">
                    <Text copyable>{String(customer.telegram_id)}</Text>
                  </Descriptions.Item>
                )}
              </Descriptions>
            </Card>

            <Card
              size="small"
              title={
                <Space>
                  <EnvironmentOutlined />
                  Yetkazib berish
                </Space>
              }
              style={{ marginTop: 16 }}
            >
              <Descriptions column={1} size="small">
                <Descriptions.Item label="Manzil">
                  {order.address ?? "—"}
                </Descriptions.Item>
                {hasCoords && (
                  <Descriptions.Item label="Xarita">
                    <Space>
                      <a
                        href={`https://maps.google.com/?q=${order.latitude},${order.longitude}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        📍 Google
                      </a>
                      <a
                        href={`https://yandex.uz/maps/?pt=${order.longitude},${order.latitude}&z=17&l=map`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Yandex
                      </a>
                    </Space>
                  </Descriptions.Item>
                )}
              </Descriptions>
            </Card>
          </Col>
        </Row>
      )}
    </Show>
  );
};
