import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, message, Space } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import axios from 'axios';

interface TemplateVariable {
  name: string;
  type: string;
  format?: string;
}

interface Template {
  _id: string;
  name: string;
  variables: TemplateVariable[];
  created_at: string;
  updated_at: string;
}

const TemplateLibrary: React.FC = () => {
  // 版式模板列表
  const [templates, setTemplates] = useState<Template[]>([]);
  // 加载状态
  const [loading, setLoading] = useState(false);
  // 模态框状态
  const [modalVisible, setModalVisible] = useState(false);
  // 编辑状态
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null);
  // 表单实例
  const [form] = Form.useForm();
  // 动态变量列表
  const [variables, setVariables] = useState<TemplateVariable[]>([]);

  // 获取版式模板列表
  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/api/templates');
      setTemplates(response.data);
    } catch (error) {
      message.error('获取版式模板失败');
      console.error('Error fetching templates:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTemplates();
  }, []);

  // 打开添加/编辑模态框
  const showModal = (template?: Template) => {
    if (template) {
      setEditingTemplate(template);
      setVariables(template.variables);
      form.setFieldsValue({
        name: template.name,
      });
    } else {
      setEditingTemplate(null);
      setVariables([{ name: '', type: 'string' }]);
      form.resetFields();
    }
    setModalVisible(true);
  };

  // 关闭模态框
  const handleCancel = () => {
    setModalVisible(false);
    setEditingTemplate(null);
    setVariables([{ name: '', type: 'string' }]);
    form.resetFields();
  };

  // 添加变量
  const addVariable = () => {
    setVariables([...variables, { name: '', type: 'string' }]);
  };

  // 删除变量
  const removeVariable = (index: number) => {
    const newVariables = [...variables];
    newVariables.splice(index, 1);
    setVariables(newVariables);
  };

  // 更新变量
  const updateVariable = (index: number, field: keyof TemplateVariable, value: string) => {
    const newVariables = [...variables];
    newVariables[index] = { ...newVariables[index], [field]: value };
    setVariables(newVariables);
  };

  // 提交表单
  const handleSubmit = async () => {
    console.log('版式模板确定按钮被点击');
    try {
      // 直接获取表单值，不使用validateFields
      const values = form.getFieldsValue();
      console.log('版式模板表单值:', values);
      
      const templateData = {
        name: values.name,
        variables: variables.filter(v => v.name.trim() !== ''),
      };
      
      let response;
      if (editingTemplate) {
        // 更新版式模板
        response = await axios.put(`http://localhost:8000/api/templates/${editingTemplate._id}`, templateData);
        message.success('更新版式模板成功');
      } else {
        // 新增版式模板
        response = await axios.post('http://localhost:8000/api/templates', templateData);
        message.success('新增版式模板成功');
      }
      
      console.log('版式模板请求成功:', response);
      handleCancel();
      fetchTemplates();
    } catch (error) {
      console.error('操作失败:', error);
      message.error('操作失败，请查看控制台日志');
    }
  };

  // 删除版式模板
  const handleDelete = async (templateId: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个版式模板吗？',
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await axios.delete(`http://localhost:8000/api/templates/${templateId}`);
          message.success('删除版式模板成功');
          fetchTemplates();
        } catch (error) {
          message.error('删除版式模板失败');
          console.error('Error deleting template:', error);
        }
      },
    });
  };

  // 表格列配置
  const columns = [
    {
      title: '模板名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '变量数量',
      dataIndex: 'variables',
      key: 'variables',
      render: (vars: TemplateVariable[]) => vars.length,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text: string) => new Date(text).toLocaleString(),
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (text: string) => new Date(text).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Template) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => showModal(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record._id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2 className="page-title">版式库管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => showModal()}>
          新建版式模板
        </Button>
      </div>
      
      <Table
        columns={columns}
        dataSource={templates}
        rowKey="_id"
        loading={loading}
        pagination={{
          pageSize: 10,
        }}
      />
      
      <Modal
        title={editingTemplate ? '编辑版式模板' : '新建版式模板'}
        open={modalVisible}
        onCancel={handleCancel}
        footer={null}
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            name="name"
            label="模板名称"
            rules={[{ required: true, message: '请输入模板名称' }]}
          >
            <Input placeholder="请输入模板名称" />
          </Form.Item>
          
          <Form.Item label="变量配置">
            <div>
              {variables.map((variable, index) => (
                <div key={index} style={{ display: 'flex', gap: 16, marginBottom: 16, alignItems: 'flex-start' }}>
                  <Form.Item
                    name={`variables[${index}].name`}
                    noStyle
                    rules={[{ required: true, message: '请输入变量名称' }]}
                  >
                    <Input
                      placeholder="变量名称"
                      value={variable.name}
                      onChange={(e) => updateVariable(index, 'name', e.target.value)}
                      style={{ width: 150 }}
                    />
                  </Form.Item>
                  
                  <Form.Item
                    name={`variables[${index}].type`}
                    noStyle
                  >
                    <select
                      value={variable.type}
                      onChange={(e) => updateVariable(index, 'type', e.target.value)}
                      style={{ width: 120, padding: '4px 8px', borderRadius: 4, border: '1px solid #d9d9d9' }}
                    >
                      <option value="string">字符串</option>
                      <option value="number">数字</option>
                      <option value="date">日期</option>
                      <option value="boolean">布尔值</option>
                    </select>
                  </Form.Item>
                  
                  <Form.Item
                    name={`variables[${index}].format`}
                    noStyle
                  >
                    <Input
                      placeholder="格式（可选）"
                      value={variable.format || ''}
                      onChange={(e) => updateVariable(index, 'format', e.target.value)}
                      style={{ width: 200 }}
                    />
                  </Form.Item>
                  
                  <Button
                    type="text"
                    danger
                    onClick={() => removeVariable(index)}
                    style={{ marginTop: 4 }}
                  >
                    删除
                  </Button>
                </div>
              ))}
              
              <Button type="dashed" onClick={addVariable} style={{ width: '100%', marginTop: 8 }}>
                添加变量
              </Button>
            </div>
          </Form.Item>
          
          <Form.Item style={{ textAlign: 'right' }}>
            <Button onClick={handleCancel} style={{ marginRight: 8 }}>
              取消
            </Button>
            <Button type="primary" onClick={handleSubmit}>
              确定
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TemplateLibrary;