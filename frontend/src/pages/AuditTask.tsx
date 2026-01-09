import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, message, Tabs, Space, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, DownloadOutlined, PlayCircleOutlined } from '@ant-design/icons';
import axios from 'axios';

const { TabPane } = Tabs;
const { Option } = Select;

interface BusinessScene {
  _id: string;
  name: string;
}

interface AuditTask {
  _id: string;
  name: string;
  scene_id: string;
  use_knowledge_base: boolean;
  status: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

interface AuditResult {
  _id: string;
  task_id: string;
  rule_id: string;
  audit_item_id: string;
  content: string;
  result: string;
  reason: string;
  ai_generated: boolean;
  edited_by?: string;
  created_at: string;
  updated_at: string;
}

interface Rule {
  _id: string;
  name: string;
}

interface AuditItem {
  _id: string;
  name: string;
}

const AuditTask: React.FC = () => {
  // 业务场景列表
  const [scenes, setScenes] = useState<BusinessScene[]>([]);
  // 规则列表
  const [rules, setRules] = useState<Rule[]>([]);
  // 审核项列表
  const [auditItems, setAuditItems] = useState<AuditItem[]>([]);
  // 审核任务列表
  const [tasks, setTasks] = useState<AuditTask[]>([]);
  // 审核结果列表
  const [results, setResults] = useState<AuditResult[]>([]);
  // 加载状态
  const [loading, setLoading] = useState(false);
  // 模态框状态
  const [taskModalVisible, setTaskModalVisible] = useState(false);
  // 编辑状态
  const [editingTask, setEditingTask] = useState<AuditTask | null>(null);
  // 表单实例
  const [taskForm] = Form.useForm();
  // 当前选中的任务ID
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);

  // 获取业务场景列表
  const fetchScenes = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/scenes');
      setScenes(response.data);
    } catch (error) {
      message.error('获取业务场景失败');
      console.error('Error fetching scenes:', error);
    }
  };

  // 获取规则列表
  const fetchRules = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/rules');
      setRules(response.data);
    } catch (error) {
      message.error('获取规则失败');
      console.error('Error fetching rules:', error);
    }
  };

  // 获取审核项列表
  const fetchAuditItems = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/audit-items');
      setAuditItems(response.data);
    } catch (error) {
      message.error('获取审核项失败');
      console.error('Error fetching audit items:', error);
    }
  };

  // 获取审核任务列表
  const fetchTasks = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/api/tasks');
      setTasks(response.data);
    } catch (error) {
      message.error('获取审核任务失败');
      console.error('Error fetching tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取审核结果列表
  const fetchResults = async (taskId: string) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/tasks/${taskId}/results`);
      setResults(response.data);
      setSelectedTaskId(taskId);
    } catch (error) {
      message.error('获取审核结果失败');
      console.error('Error fetching results:', error);
    }
  };

  useEffect(() => {
    fetchScenes();
    fetchRules();
    fetchAuditItems();
    fetchTasks();
  }, []);

  // 创建/编辑审核任务
  const showTaskModal = async (task?: AuditTask) => {
    // 重新获取业务场景列表，确保与业务场景管理页面一致
    await fetchScenes();
    
    if (task) {
      setEditingTask(task);
      taskForm.setFieldsValue(task);
    } else {
      setEditingTask(null);
      taskForm.resetFields();
    }
    setTaskModalVisible(true);
  };

  const handleTaskCancel = () => {
    setTaskModalVisible(false);
    setEditingTask(null);
    taskForm.resetFields();
  };

  const handleTaskSubmit = async () => {
    console.log('审核任务确定按钮被点击');
    try {
      // 直接获取表单值，不使用validateFields
      const values = taskForm.getFieldsValue();
      console.log('审核任务表单值:', values);
      
      let response;
      if (editingTask) {
        // 更新审核任务
        response = await axios.put(`http://localhost:8000/api/tasks/${editingTask._id}`, values);
        message.success('更新审核任务成功');
      } else {
        // 新增审核任务
        response = await axios.post('http://localhost:8000/api/tasks', values);
        message.success('新增审核任务成功');
      }
      
      console.log('审核任务请求成功:', response);
      handleTaskCancel();
      fetchTasks();
    } catch (error) {
      console.error('审核任务操作失败:', error);
      message.error('操作失败，请查看控制台日志');
    }
  };

  // 运行审核任务
  const runTask = async (taskId: string) => {
    try {
      await axios.post(`http://localhost:8000/api/tasks/${taskId}/run`);
      message.success('审核任务已开始');
      // 重新获取任务列表
      fetchTasks();
    } catch (error) {
      message.error('运行审核任务失败');
      console.error('Error running task:', error);
    }
  };

  // 删除审核任务
  const handleTaskDelete = async (taskId: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个审核任务吗？',
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await axios.delete(`http://localhost:8000/api/tasks/${taskId}`);
          message.success('删除审核任务成功');
          fetchTasks();
          // 如果当前选中的任务被删除，清空结果列表
          if (selectedTaskId === taskId) {
            setResults([]);
            setSelectedTaskId(null);
          }
        } catch (error) {
          message.error('删除审核任务失败');
          console.error('Error deleting task:', error);
        }
      },
    });
  };

  // 下载审核结果
  const downloadResults = async (taskId: string) => {
    try {
      const response = await axios.post(`http://localhost:8000/api/tasks/${taskId}/download`, {}, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `audit-results-${taskId}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      message.success('下载审核结果成功');
    } catch (error) {
      message.error('下载审核结果失败');
      console.error('Error downloading results:', error);
    }
  };

  // 获取状态标签
  const getStatusTag = (status: string) => {
    switch (status) {
      case 'pending':
        return <Tag color="blue">待处理</Tag>;
      case 'running':
        return <Tag color="orange">运行中</Tag>;
      case 'completed':
        return <Tag color="green">已完成</Tag>;
      case 'failed':
        return <Tag color="red">失败</Tag>;
      default:
        return <Tag color="gray">未知</Tag>;
    }
  };

  // 获取审核结果标签
  const getResultTag = (result: string) => {
    switch (result) {
      case 'pass':
        return <Tag color="green">通过</Tag>;
      case 'fail':
        return <Tag color="red">失败</Tag>;
      case 'warning':
        return <Tag color="orange">警告</Tag>;
      default:
        return <Tag color="gray">未知</Tag>;
    }
  };

  // 审核任务表格列配置
  const taskColumns = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '所属场景',
      dataIndex: 'scene_id',
      key: 'scene_id',
      render: (sceneId: string) => {
        const scene = scenes.find(s => s._id === sceneId);
        return scene ? scene.name : sceneId;
      },
    },
    {
      title: '关联知识库',
      dataIndex: 'use_knowledge_base',
      key: 'use_knowledge_base',
      render: (useKB: boolean) => useKB ? '是' : '否',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text: string) => new Date(text).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: AuditTask) => (
        <Space>
          <Button
            type="link"
            icon={<PlayCircleOutlined />}
            onClick={() => runTask(record._id)}
            disabled={record.status === 'running' || record.status === 'completed'}
          >
            运行
          </Button>
          <Button
            type="link"
            icon={<DownloadOutlined />}
            onClick={() => downloadResults(record._id)}
            disabled={record.status !== 'completed'}
          >
            下载
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleTaskDelete(record._id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  // 审核结果表格列配置
  const resultColumns = [
    {
      title: '审核项',
      dataIndex: 'audit_item_id',
      key: 'audit_item_id',
      render: (itemId: string) => {
        const item = auditItems.find(i => i._id === itemId);
        return item ? item.name : itemId;
      },
    },
    {
      title: '规则',
      dataIndex: 'rule_id',
      key: 'rule_id',
      render: (ruleId: string) => {
        const rule = rules.find(r => r._id === ruleId);
        return rule ? rule.name : ruleId;
      },
    },
    {
      title: '审核内容',
      dataIndex: 'content',
      key: 'content',
    },
    {
      title: '审核结果',
      dataIndex: 'result',
      key: 'result',
      render: (result: string) => getResultTag(result),
    },
    {
      title: '审核理由',
      dataIndex: 'reason',
      key: 'reason',
    },
    {
      title: 'AI生成',
      dataIndex: 'ai_generated',
      key: 'ai_generated',
      render: (aiGenerated: boolean) => aiGenerated ? '是' : '否',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: AuditResult) => (
        <Button type="link" icon={<EditOutlined />} onClick={() => console.log('Edit result:', record)}>
          编辑
        </Button>
      ),
    },
  ];

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#FFFFFF',
      padding: '24px'
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '24px',
        padding: '16px 0'
      }}>

        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={() => showTaskModal()}
          style={{
            backgroundColor: '#6750A4',
            border: 'none',
            borderRadius: '8px',
            color: '#FFFFFF'
          }}
        >
          新建审核任务
        </Button>
      </div>
      
      <Tabs 
        defaultActiveKey="tasks"
        style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '12px',
          padding: '16px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
          border: '1px solid #79747E'
        }}
        tabBarStyle={{
          marginBottom: '20px'
        }}
      >
        {/* 审核任务列表 */}
        <TabPane 
          tab={<span style={{ color: '#1C1B1F', fontSize: '15px', fontWeight: 500 }}>任务列表</span>} 
          key="tasks"
        >
          <Table
            columns={taskColumns}
            dataSource={tasks}
            rowKey="_id"
            loading={loading}
            pagination={{
              pageSize: 10,
              style: {
                marginTop: '20px',
                color: '#49454F'
              }
            }}
            onRow={(record) => ({
              onClick: () => {
                if (record.status === 'completed') {
                  fetchResults(record._id);
                }
              },
              style: {
                cursor: record.status === 'completed' ? 'pointer' : 'default',
                '&:hover': {
                  backgroundColor: '#F3EDF7'
                }
              }
            })}
            style={{
              backgroundColor: '#FFFFFF'
            }}
            bordered={false}
            components={{
              header: {
                cell: (props: any) => (
                  <th {...props} style={{
                    backgroundColor: '#F3EDF7',
                    color: '#1C1B1F',
                    fontWeight: 600,
                    borderBottom: '1px solid #79747E'
                  }} />
                )
              },
              body: {
                cell: (props: any) => (
                  <td {...props} style={{
                    color: '#49454F',
                    borderBottom: '1px solid #E7E0EC'
                  }} />
                )
              }
            }}
          />
        </TabPane>
        
        {/* 审核结果 */}
        <TabPane 
          tab={<span style={{ color: '#1C1B1F', fontSize: '15px', fontWeight: 500 }}>审核结果</span>} 
          key="results"
        >
          {selectedTaskId ? (
            <>
              <div style={{ 
                marginBottom: '20px',
                padding: '12px 16px',
                backgroundColor: '#E8DEF8',
                borderRadius: '8px',
                border: '1px solid #79747E'
              }}>
                <strong style={{ color: '#1C1B1F' }}>任务ID:</strong> <span style={{ color: '#49454F' }}>{selectedTaskId}</span>
              </div>
              <Table
                columns={resultColumns}
                dataSource={results}
                rowKey="_id"
                pagination={{
                  pageSize: 10,
                  style: {
                    marginTop: '20px',
                    color: '#49454F'
                  }
                }}
                style={{
                  backgroundColor: '#FFFFFF'
                }}
                bordered={false}
                components={{
                  header: {
                    cell: (props: any) => (
                      <th {...props} style={{
                        backgroundColor: '#F3EDF7',
                        color: '#1C1B1F',
                        fontWeight: 600,
                        borderBottom: '1px solid #79747E'
                      }} />
                    )
                  },
                  body: {
                    cell: (props: any) => (
                      <td {...props} style={{
                        color: '#49454F',
                        borderBottom: '1px solid #E7E0EC'
                      }} />
                    )
                  }
                }}
              />
            </>
          ) : (
            <div style={{ 
              padding: '60px 20px', 
              textAlign: 'center', 
              color: '#49454F',
              fontSize: '15px',
              backgroundColor: '#E7E0EC',
              borderRadius: '8px',
              border: '1px solid #79747E',
              margin: '20px 0'
            }}>
              请选择一个已完成的审核任务查看结果
            </div>
          )}
        </TabPane>
      </Tabs>
      
      {/* 审核任务模态框 */}
      <Modal
        title={<span style={{ color: '#1C1B1F', fontSize: '18px', fontWeight: 600 }}>{editingTask ? '编辑审核任务' : '新建审核任务'}</span>}
        open={taskModalVisible}
        onCancel={handleTaskCancel}
        footer={null}
        style={{
          top: '10%'
        }}
        bodyStyle={{
          backgroundColor: '#FFFBFE',
          borderRadius: '12px'
        }}
        wrapClassName="custom-modal"
      >
        <Form
          form={taskForm}
          layout="vertical"
          style={{
            backgroundColor: '#FFFBFE',
            padding: '16px 0'
          }}
        >
          <Form.Item
            name="name"
            label={<span style={{ color: '#1C1B1F', fontWeight: 500 }}>任务名称</span>}
            rules={[{ required: true, message: '请输入任务名称' }]}
            style={{
              marginBottom: '20px'
            }}
          >
            <Input 
              placeholder="请输入任务名称" 
              style={{
                backgroundColor: '#E7E0EC',
                border: '1px solid #79747E',
                borderRadius: '8px',
                color: '#1C1B1F'
              }}
            />
          </Form.Item>
          <Form.Item
            name="scene_id"
            label={<span style={{ color: '#1C1B1F', fontWeight: 500 }}>选择业务场景</span>}
            rules={[{ required: true, message: '请选择业务场景' }]}
            style={{
              marginBottom: '20px'
            }}
          >
            <Select 
              placeholder="请选择业务场景"
              style={{
                backgroundColor: '#E7E0EC',
                border: '1px solid #79747E',
                borderRadius: '8px',
                color: '#1C1B1F'
              }}
            >
              {scenes.map(scene => (
                <Option 
                  key={scene._id} 
                  value={scene._id}
                  style={{
                    color: '#1C1B1F'
                  }}
                >{scene.name}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="use_knowledge_base"
            label={<span style={{ color: '#1C1B1F', fontWeight: 500 }}>关联知识库</span>}
            style={{
              marginBottom: '24px'
            }}
          >
            <Select 
              placeholder="请选择是否关联知识库"
              style={{
                backgroundColor: '#E7E0EC',
                border: '1px solid #79747E',
                borderRadius: '8px',
                color: '#1C1B1F'
              }}
            >
              <Option 
                value={true}
                style={{
                  color: '#1C1B1F'
                }}
              >是</Option>
              <Option 
                value={false}
                style={{
                  color: '#1C1B1F'
                }}
              >否</Option>
            </Select>
          </Form.Item>
          <Form.Item style={{ textAlign: 'right', marginBottom: 0 }}>
            <Button 
              onClick={handleTaskCancel} 
              style={{ 
                marginRight: '12px',
                backgroundColor: '#F3EDF7',
                border: '1px solid #79747E',
                color: '#1C1B1F',
                borderRadius: '8px'
              }}
            >
              取消
            </Button>
            <Button 
              type="primary" 
              onClick={handleTaskSubmit}
              style={{
                backgroundColor: '#6750A4',
                border: 'none',
                borderRadius: '8px',
                color: '#FFFFFF'
              }}
            >
              确定
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AuditTask;