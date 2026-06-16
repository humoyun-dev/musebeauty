import { Authenticated, Refine } from "@refinedev/core";
import {
  ErrorComponent,
  ThemedLayoutV2,
  ThemedTitleV2,
  useNotificationProvider,
} from "@refinedev/antd";
import "@refinedev/antd/dist/reset.css";
import routerProvider, {
  CatchAllNavigate,
  DocumentTitleHandler,
  NavigateToResource,
  UnsavedChangesNotifier,
} from "@refinedev/react-router-v6";
import {
  ShoppingOutlined,
  ProfileOutlined,
  CreditCardOutlined,
  InboxOutlined,
  TeamOutlined,
  AppstoreOutlined,
  DashboardOutlined,
  TagsOutlined,
  GiftOutlined,
} from "@ant-design/icons";
import { App as AntdApp, ConfigProvider } from "antd";
import { BrowserRouter, Outlet, Route, Routes } from "react-router-dom";

import { authProvider } from "./providers/authProvider";
import { dataProvider } from "./providers/dataProvider";
import { Login } from "./pages/login";
import { Dashboard } from "./pages/dashboard";
import { ProductList, ProductCreate, ProductEdit } from "./pages/products";
import { CategoryList, CategoryCreate, CategoryEdit } from "./pages/categories";
import { OrderList, OrderShow } from "./pages/orders";
import { PaymentList } from "./pages/payments";
import { SupplyList, SupplyCreate } from "./pages/supply";
import { CustomerList } from "./pages/customers";
import { DiscountList, DiscountCreate, DiscountEdit } from "./pages/discounts";
import { PromoList, PromoCreate, PromoEdit } from "./pages/promos";

export const App = () => {
  return (
    <BrowserRouter>
      <ConfigProvider
        theme={{
          token: {
            colorPrimary: "#d6336c",
            colorLink: "#d6336c",
            borderRadius: 8,
            fontSize: 14,
          },
        }}
      >
        <AntdApp>
          <Refine
            dataProvider={dataProvider}
            authProvider={authProvider}
            routerProvider={routerProvider}
            notificationProvider={useNotificationProvider}
            resources={[
              {
                name: "dashboard",
                list: "/",
                meta: { label: "Boshqaruv", icon: <DashboardOutlined /> },
              },
              {
                name: "orders",
                list: "/orders",
                show: "/orders/show/:id",
                meta: { label: "Buyurtmalar", icon: <ProfileOutlined /> },
              },
              {
                name: "payments",
                list: "/payments",
                meta: { label: "To'lovlar", icon: <CreditCardOutlined /> },
              },
              {
                name: "products",
                list: "/products",
                create: "/products/create",
                edit: "/products/edit/:id",
                meta: { label: "Mahsulotlar", icon: <ShoppingOutlined /> },
              },
              {
                name: "categories",
                list: "/categories",
                create: "/categories/create",
                edit: "/categories/edit/:id",
                meta: { label: "Kategoriyalar", icon: <AppstoreOutlined /> },
              },
              {
                name: "supply-batches",
                list: "/supply-batches",
                create: "/supply-batches/create",
                meta: { label: "Ombor / Partiyalar", icon: <InboxOutlined /> },
              },
              {
                name: "discounts",
                list: "/discounts",
                create: "/discounts/create",
                edit: "/discounts/edit/:id",
                meta: { label: "Chegirmalar", icon: <TagsOutlined /> },
              },
              {
                name: "promo-codes",
                list: "/promo-codes",
                create: "/promo-codes/create",
                edit: "/promo-codes/edit/:id",
                meta: { label: "Promokodlar", icon: <GiftOutlined /> },
              },
              {
                name: "customers",
                list: "/customers",
                meta: { label: "Mijozlar", icon: <TeamOutlined /> },
              },
            ]}
            options={{
              syncWithLocation: true,
              warnWhenUnsavedChanges: true,
            }}
          >
            <Routes>
              <Route
                element={
                  <Authenticated
                    key="authenticated-routes"
                    fallback={<CatchAllNavigate to="/login" />}
                  >
                    <ThemedLayoutV2
                      Title={({ collapsed }) => (
                        <ThemedTitleV2
                          collapsed={collapsed}
                          text="MUSE BEAUTY"
                        />
                      )}
                    >
                      <Outlet />
                    </ThemedLayoutV2>
                  </Authenticated>
                }
              >
                <Route index element={<Dashboard />} />

                <Route path="/orders">
                  <Route index element={<OrderList />} />
                  <Route path="show/:id" element={<OrderShow />} />
                </Route>

                <Route path="/payments" element={<PaymentList />} />

                <Route path="/products">
                  <Route index element={<ProductList />} />
                  <Route path="create" element={<ProductCreate />} />
                  <Route path="edit/:id" element={<ProductEdit />} />
                </Route>

                <Route path="/categories">
                  <Route index element={<CategoryList />} />
                  <Route path="create" element={<CategoryCreate />} />
                  <Route path="edit/:id" element={<CategoryEdit />} />
                </Route>

                <Route path="/supply-batches">
                  <Route index element={<SupplyList />} />
                  <Route path="create" element={<SupplyCreate />} />
                </Route>

                <Route path="/discounts">
                  <Route index element={<DiscountList />} />
                  <Route path="create" element={<DiscountCreate />} />
                  <Route path="edit/:id" element={<DiscountEdit />} />
                </Route>

                <Route path="/promo-codes">
                  <Route index element={<PromoList />} />
                  <Route path="create" element={<PromoCreate />} />
                  <Route path="edit/:id" element={<PromoEdit />} />
                </Route>

                <Route path="/customers" element={<CustomerList />} />

                <Route path="*" element={<ErrorComponent />} />
              </Route>

              <Route
                element={
                  <Authenticated key="auth-pages" fallback={<Outlet />}>
                    <NavigateToResource resource="dashboard" />
                  </Authenticated>
                }
              >
                <Route path="/login" element={<Login />} />
              </Route>
            </Routes>

            <UnsavedChangesNotifier />
            <DocumentTitleHandler />
          </Refine>
        </AntdApp>
      </ConfigProvider>
    </BrowserRouter>
  );
};
