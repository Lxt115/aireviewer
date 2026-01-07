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
  // 低饱和度主题配置
  const lowSaturationTheme = {
    token: {
      // 主色调 - 低饱和度蓝色
      colorPrimary: '#5a7da3',
      colorPrimaryHover: '#6b8db8',
      colorPrimaryActive: '#4a6d98',
      colorPrimaryBorder: '#c4d4e3',
      
      // 文本色
      colorText: '#333333',
      colorTextSecondary: '#666666',
      colorTextTertiary: '#999999',
      
      // 背景色
      colorBgContainer: '#f5f7fa',
      colorBgElevated: '#ffffff',
      colorBgLayout: '#f0f2f5',
      
      // 边框色
      colorBorder: '#e0e0e0',
      colorBorderSecondary: '#f0f0f0',
      
      // 成功色 - 低饱和度绿色
      colorSuccess: '#67c23a',
      colorSuccessHover: '#7ec261',
      colorSuccessActive: '#529b2e',
      
      // 警告色 - 低饱和度黄色
      colorWarning: '#e6a23c',
      colorWarningHover: '#ebb563',
      colorWarningActive: '#cf9236',
      
      // 错误色 - 低饱和度红色
      colorError: '#f56c6c',
      colorErrorHover: '#f78989',
      colorErrorActive: '#e65252',
      
      // 信息色 - 低饱和度蓝色
      colorInfo: '#909399',
      colorInfoHover: '#a6a9ad',
      colorInfoActive: '#73767a',
      
      // 卡片阴影
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
      boxShadowSecondary: '0 4px 16px rgba(0, 0, 0, 0.08)',
      
      // 圆角
      borderRadius: 4,
      borderRadiusLG: 8,
      borderRadiusSM: 2,
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
    <ConfigProvider theme={lowSaturationTheme}>
      <Layout>
        <Header style={{ padding: 0, background: '#fff', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ padding: '0 24px', fontSize: 18, fontWeight: 500 }}>
            基于规则的大模型多模态智能审核平台
          </div>
          <Button 
            type="primary" 
            icon={<KeyOutlined />} 
            onClick={() => {
              fetchApiConfig();
              setApiConfigModalVisible(true);
            }}
            style={{ marginRight: 24 }}
          >
            配置大模型API
          </Button>
        </Header>
        <Content style={{ margin: '24px', padding: 24, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)' }}>
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