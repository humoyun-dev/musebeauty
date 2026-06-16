import { useCustom } from "@refinedev/core";
import {
  Card,
  Col,
  List as AntList,
  Row,
  Spin,
  Statistic,
  Tag,
  Typography,
} from "antd";
import {
  DollarOutlined,
  RiseOutlined,
  ShoppingCartOutlined,
  TeamOutlined,
  WalletOutlined,
  WarningOutlined,
} from "@ant-design/icons";

import { money } from "../lib/format";

const { Title, Text } = Typography;

interface DashboardData {
  today: { orders_count: number; revenue: number; profit: number };
  month: { orders_count: number; revenue: number; profit: number };
  total_customers: number;
  active_products: number;
  low_stock_count: number;
  pending_payments: number;
}

interface TopProduct {
  product_id: number;
  name: string;
  qty_sold: number;
  revenue: number;
}

export const Dashboard = () => {
  const { data, isLoading } = useCustom<DashboardData>({
    url: "/reports/dashboard",
    method: "get",
  });
  const { data: topData } = useCustom<TopProduct[]>({
    url: "/reports/top-products",
    method: "get",
    config: { query: { limit: 5, days: 30 } },
  });

  const d = data?.data;
  const tops = topData?.data ?? [];

  if (isLoading || !d) {
    return (
      <div style={{ textAlign: "center", padding: 64 }}>
        <Spin size="large" />
      </div>
    );
  }

  const rankColors = ["gold", "#bfbfbf", "#d48806"];

  return (
    <div>
      <Title level={3}>Boshqaruv paneli</Title>

      {/* Bugun */}
      <Text type="secondary">Bugun</Text>
      <Row gutter={[16, 16]} style={{ marginTop: 8 }}>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="Buyurtmalar"
              value={d.today.orders_count}
              prefix={<ShoppingCartOutlined style={{ color: "#d6336c" }} />}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="Daromad"
              value={money(d.today.revenue)}
              prefix={<DollarOutlined style={{ color: "#1677ff" }} />}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="Foyda"
              value={money(d.today.profit)}
              valueStyle={{ color: "#3f8600" }}
              prefix={<RiseOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="Kutilayotgan to'lovlar"
              value={d.pending_payments}
              valueStyle={{ color: d.pending_payments > 0 ? "#fa8c16" : undefined }}
              prefix={<WalletOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* Oy + umumiy */}
      <Text type="secondary">Shu oy</Text>
      <Row gutter={[16, 16]} style={{ marginTop: 8 }}>
        <Col xs={12} md={6}>
          <Card>
            <Statistic title="Oylik daromad" value={money(d.month.revenue)} />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="Oylik foyda"
              value={money(d.month.profit)}
              valueStyle={{ color: "#3f8600" }}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="Mijozlar"
              value={d.total_customers}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="Kam qolgan mahsulot"
              value={d.low_stock_count}
              valueStyle={{ color: d.low_stock_count > 0 ? "#cf1322" : undefined }}
              prefix={
                d.low_stock_count > 0 ? (
                  <WarningOutlined style={{ color: "#cf1322" }} />
                ) : undefined
              }
            />
          </Card>
        </Col>
      </Row>

      <Card title="Eng ko'p sotilgan (30 kun)" style={{ marginTop: 16 }}>
        <AntList
          dataSource={tops}
          locale={{ emptyText: "Hali sotuv yo'q" }}
          renderItem={(item, i) => (
            <AntList.Item>
              <span>
                <Tag
                  color={rankColors[i] ?? "default"}
                  style={{ marginRight: 8 }}
                >
                  {i + 1}
                </Tag>
                {item.name}
              </span>
              <span>
                <Text type="secondary">{item.qty_sold} dona</Text>
                {" · "}
                <Text strong>{money(item.revenue)}</Text>
              </span>
            </AntList.Item>
          )}
        />
      </Card>
    </div>
  );
};
