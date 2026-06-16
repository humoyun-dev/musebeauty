import { List, useTable } from "@refinedev/antd";
import { Table, Typography } from "antd";

import { dateTime } from "../lib/format";

const { Text } = Typography;

interface ICustomer {
  id: number;
  telegram_id: number;
  name?: string;
  phone?: string;
  created_at: string;
}

export const CustomerList = () => {
  const { tableProps } = useTable<ICustomer>({ syncWithLocation: true });
  return (
    <List title="Mijozlar">
      <Table {...tableProps} rowKey="id">
        <Table.Column dataIndex="id" title="#" width={60} />
        <Table.Column
          dataIndex="name"
          title="Ism"
          render={(v?: string) => v || <Text type="secondary">Noma'lum</Text>}
        />
        <Table.Column
          dataIndex="phone"
          title="Telefon"
          render={(v?: string) =>
            v ? <a href={`tel:${v}`}>{v}</a> : <Text type="secondary">—</Text>
          }
        />
        <Table.Column
          dataIndex="telegram_id"
          title="Telegram ID"
          render={(v: number) => (
            <Text copyable style={{ fontSize: 13 }}>
              {String(v)}
            </Text>
          )}
        />
        <Table.Column
          dataIndex="created_at"
          title="Ro'yxatdan o'tgan"
          render={(v: string) => dateTime(v)}
        />
      </Table>
    </List>
  );
};
