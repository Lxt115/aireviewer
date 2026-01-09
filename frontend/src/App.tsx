import React, { useState } from 'react';
import { Layout, Tabs, Button, Modal, Input, Form, Select, message, ConfigProvider } from 'antd';
import { SettingOutlined, FileTextOutlined, TagOutlined, KeyOutlined } from '@ant-design/icons';
import axios from 'axios';

// 页面组件
import AuditTask from './pages/AuditTask';
import TemplateLibrary from './pages/TemplateLibrary';
import FullFlowDebug from './pages/FullFlowDebug';

const { Header, Content } = Layout;

const App: React.FC = () => {
  // 设计系统主题配置
  const designSystemTheme = {
    token: {
      // 主色调 - 紫色系
      colorPrimary: '#6750A4',
      colorPrimaryHover: '#5A469A',
      colorPrimaryActive: '#4B3B87',
      colorPrimaryBorder: '#79747E',
      
      // 文本色
      colorText: '#1C1B1F',
      colorTextSecondary: '#49454F',
      colorTextTertiary: '#79747E',
      
      // 背景色
      colorBgContainer: '#FFFFFF',
      colorBgElevated: '#FFFFFF',
      colorBgLayout: '#FFFBFE',
      
      // 边框色
      colorBorder: '#79747E',
      colorBorderSecondary: '#F3EDF7',
      
      // 成功色
      colorSuccess: '#6750A4',
      colorSuccessHover: '#5A469A',
      colorSuccessActive: '#4B3B87',
      
      // 警告色
      colorWarning: '#F3EDF7',
      colorWarningHover: '#E8DEF8',
      colorWarningActive: '#D0BCFF',
      
      // 错误色
      colorError: '#7D5260',
      colorErrorHover: '#6D4A56',
      colorErrorActive: '#5D4046',
      
      // 信息色
      colorInfo: '#5A469A',
      colorInfoHover: '#4B3B87',
      colorInfoActive: '#3C2A75',
      
      // 卡片阴影
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      boxShadowSecondary: '0 4px 16px rgba(0, 0, 0, 0.12)',
      
      // 圆角
      borderRadius: 8,
      borderRadiusLG: 12,
      borderRadiusSM: 6,
    },
  };

  // 标签页状态管理
  const [activeKey, setActiveKey] = useState('full-flow-debug');

  // API配置状态
  const [apiConfigModalVisible, setApiConfigModalVisible] = useState(false);
  const [form] = Form.useForm();

  // 标签页切换处理函数
  const handleTabChange = (key: string) => {
    setActiveKey(key);
  };

  // 获取当前API配置
  const fetchApiConfig = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/config/ai');
      form.setFieldsValue(response.data);
    } catch (error) {
      message.error('获取API配置失败');
      console.error('Error fetching API config:', error);
    }
  };

  // 保存API配置
  const handleSaveApiConfig = async () => {
    console.log('API配置保存按钮被点击');
    try {
      // 直接获取表单值，不使用validateFields
      const values = form.getFieldsValue();
      console.log('API配置表单值:', values);
      await axios.post('http://localhost:8000/api/config/ai', values);
      message.success('API配置保存成功');
      setApiConfigModalVisible(false);
    } catch (error) {
      console.error('保存API配置失败:', error);
      message.error('保存API配置失败，请查看控制台日志');
    }
  };

  return (
    <ConfigProvider theme={designSystemTheme}>
      <Layout>
        <Header style={{ padding: 0, background: '#fff', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ padding: '0 24px', fontSize: 18, fontWeight: 500 }}>
            智能审核平台
          </div>
          <Button 
            type="default" 
            icon={<KeyOutlined />} 
            onClick={() => {
              fetchApiConfig();
              setApiConfigModalVisible(true);
            }}
            style={{ 
              marginRight: 24,
              backgroundColor: '#F3EDF7',
              border: '1px solid #79747E',
              borderRadius: '8px',
              color: '#1C1B1F'
            }}
          >
            配置大模型API
          </Button>
        </Header>
        <Content style={{ margin: 0, padding: 0, background: 'transparent' }}>
          <Tabs
            activeKey={activeKey}
            onChange={handleTabChange}
            items={[
              {
                key: 'full-flow-debug',
                label: (
                  <span>
                    <SettingOutlined />
                    全流程调试
                  </span>
                ),
                children: <FullFlowDebug />,
              },
              {
                key: 'audit-task',
                label: (
                  <span>
                    <TagOutlined />
                    审核任务流
                  </span>
                ),
                children: <AuditTask />,
              },
              {
                key: 'template-library',
                label: (
                  <span>
                    <FileTextOutlined />
                    版式库管理
                  </span>
                ),
                children: <TemplateLibrary />,
              },
            ]}
            style={{
              backgroundColor: '#FFFFFF',
              borderRadius: '0',
              boxShadow: 'none',
              border: 'none'
            }}
            tabBarStyle={{
              borderBottom: '1px solid #79747E',
              padding: '0 24px'
            }}
          />
        </Content>

        {/* API配置模态框 */}
        <Modal
          title="大模型API配置"
          open={apiConfigModalVisible}
          onCancel={() => setApiConfigModalVisible(false)}
          footer={null}
          width={600}
        >
          <Form
            form={form}
            layout="vertical"
          >
            <Form.Item
              name="provider"
              label="AI提供商"
              rules={[{ required: true, message: '请选择AI提供商' }]}
            >
              <Select placeholder="请选择AI提供商">
                <Select.Option value="openai">OpenAI</Select.Option>
                <Select.Option value="dashscope">阿里云百炼</Select.Option>
              </Select>
            </Form.Item>
            <Form.Item
              name="api_key"
              label="API Key"
              rules={[{ required: true, message: '请输入API Key' }]}
            >
              <Input.Password placeholder="请输入API Key" />
            </Form.Item>
            <Form.Item
              name="base_url"
              label="API地址"
              rules={[{ required: true, message: '请输入API地址' }]}
            >
              <Input placeholder="请输入API地址" />
            </Form.Item>
            <Form.Item
              name="model"
              label="模型名称"
              rules={[{ required: true, message: '请输入模型名称' }]}
            >
              <Input placeholder="请输入模型名称" />
            </Form.Item>
            <Form.Item style={{ textAlign: 'right' }}>
              <Button onClick={() => setApiConfigModalVisible(false)} style={{ marginRight: 8 }}>
                取消
              </Button>
              <Button type="primary" onClick={handleSaveApiConfig}>
                保存
              </Button>
            </Form.Item>
          </Form>
        </Modal>
      </Layout>
    </ConfigProvider>
  );
};

export default App;