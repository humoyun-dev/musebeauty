import { useCustomMutation, useInvalidate } from "@refinedev/core";
import { List, useTable } from "@refinedev/antd";
import { useNavigation } from "@refinedev/core";
import { Button, Image, Space, Table, Tag, message } from "antd";

import { dateTime, money } from "../lib/format";

interface IPayment {
  id: number;
  order_id: number;
  amount: number;
  method: string;
  screenshot_url?: string;
  is_confirmed: boolean;
  created_at: string;
}

export const PaymentList = () => {
  const { tableProps } = useTable<IPayment>({
    syncWithLocation: true,
    sorters: { initial: [{ field: "id", order: "desc" }] },
  });
  const { mutate, isLoading } = useCustomMutation();
  const invalidate = useInvalidate();
  const { show } = useNavigation();

  const confirm = (id: number) => {
    mutate(
      { url: `/payments/${id}/confirm`, method: "post", values: {} },
      {
        onSuccess: () => {
          message.success("To'lov tasdiqlandi, buyurtma 'to'landi'ga o'tdi");
          invalidate({ resource: "payments", invalidates: ["list"] });
        },
        onError: (e: any) => message.error(e?.message ?? "Xatolik"),
      },
    );
  };

  return (
    <List title="To'lovlar (cheklar)">
      <Table {...tableProps} rowKey="id">
        <Table.Column dataIndex="id" title="#" width={50} />
        <Table.Column
          dataIndex="order_id"
          title="Buyurtma"
          render={(v: number) => (
            <a onClick={() => show("orders", v)}>Buyurtma #{v}</a>
          )}
        />
        <Table.Column
          dataIndex="amount"
          title="Summa"
          align="right"
          render={(v) => money(v)}
        />
        <Table.Column dataIndex="method" title="Usul" />
        <Table.Column
          dataIndex="screenshot_url"
          title="Chek"
          render={(v?: string) =>
            v ? (
              <Image
                src={v}
                width={48}
                height={48}
                style={{ objectFit: "cover", borderRadius: 6 }}
              />
            ) : (
              "—"
            )
          }
        />
        <Table.Column
          dataIndex="created_at"
          title="Sana"
          render={(v: string) => dateTime(v)}
        />
        <Table.Column
          dataIndex="is_confirmed"
          title="Holat"
          render={(v: boolean) => (
            <Tag color={v ? "green" : "orange"}>
              {v ? "Tasdiqlangan" : "Kutilmoqda"}
            </Tag>
          )}
        />
        <Table.Column<IPayment>
          title="Amal"
          render={(_, record) => (
            <Space>
              <Button
                type="primary"
                size="small"
                disabled={record.is_confirmed}
                loading={isLoading}
                onClick={() => confirm(record.id)}
              >
                Tasdiqlash
              </Button>
            </Space>
          )}
        />
      </Table>
    </List>
  );
};
