import { useLogin } from "@refinedev/core";
import { Button, Card, Form, Input, Typography } from "antd";

const { Title, Text } = Typography;

interface LoginForm {
  username: string;
  password: string;
}

export const Login = () => {
  const { mutate: login, isLoading } = useLogin<LoginForm>();

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#fff0f4",
      }}
    >
      <Card style={{ width: 360 }}>
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <Title level={3} style={{ margin: 0, color: "#d6336c" }}>
            MUSE BEAUTY
          </Title>
          <Text type="secondary">Admin panel</Text>
        </div>
        <Form<LoginForm>
          layout="vertical"
          onFinish={(values) => login(values)}
          requiredMark={false}
        >
          <Form.Item
            label="Login"
            name="username"
            rules={[{ required: true, message: "Login kiriting" }]}
          >
            <Input size="large" placeholder="admin" autoComplete="username" />
          </Form.Item>
          <Form.Item
            label="Parol"
            name="password"
            rules={[{ required: true, message: "Parol kiriting" }]}
          >
            <Input.Password
              size="large"
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            size="large"
            block
            loading={isLoading}
          >
            Kirish
          </Button>
        </Form>
      </Card>
    </div>
  );
};
