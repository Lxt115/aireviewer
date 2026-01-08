import React, { useState, useEffect } from 'react';
import { Button, Modal, Form, Input, Select, message, Card } from 'antd';
import {
  PlusOutlined, EditOutlined, DeleteOutlined, UploadOutlined, PlayCircleOutlined,
  CheckCircleOutlined, MessageOutlined, MinusOutlined
} from '@ant-design/icons';
import axios from 'axios';

// 业务场景接口
interface BusinessScene {
  _id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

// 规则接口
interface Rule {
  _id: string;
  name: string;
  scene_id: string;
  description: string;
  created_at: string;
  updated_at: string;
}

// 审核项接口
interface AuditItem {
  _id: string;
  name: string;
  rule_id: string;
  type: string;
  criteria: string;
  created_at: string;
  updated_at: string;
}

// 文件上传接口
interface UploadFile {
  uid: string;
  name: string;
  status?: 'done' | 'error' | 'uploading' | 'removed';
  response?: any;
  url?: string;
}

const FullFlowDebug: React.FC = () => {
  // 状态管理
  const [scenes, setScenes] = useState<BusinessScene[]>([]);
  const [rules, setRules] = useState<Rule[]>([]);
  const [auditItems, setAuditItems] = useState<AuditItem[]>([]);
  
  // 选中状态
  const [selectedScene, setSelectedScene] = useState<string>('');
  const [selectedRule, setSelectedRule] = useState<string>('');
  
  // 模态框状态
  const [sceneModalVisible, setSceneModalVisible] = useState(false);
  const [ruleModalVisible, setRuleModalVisible] = useState(false);
  const [itemModalVisible, setItemModalVisible] = useState(false);
  
  // 编辑状态
  const [editingScene, setEditingScene] = useState<BusinessScene | null>(null);
  const [editingRule, setEditingRule] = useState<Rule | null>(null);
  const [editingItem, setEditingItem] = useState<AuditItem | null>(null);
  
  // 业务场景表单状态
  const [sceneName, setSceneName] = useState('');
  const [sceneDescription, setSceneDescription] = useState('');
  
  // 规则表单状态
  const [ruleName, setRuleName] = useState('');
  const [ruleSceneId, setRuleSceneId] = useState('');
  // 新增规则直接编辑状态
  const [showNewRuleInput, setShowNewRuleInput] = useState(false);
  const [newRuleName, setNewRuleName] = useState('');
  
  // 审核项表单状态
  const [itemName, setItemName] = useState('');
  const [itemRuleId, setItemRuleId] = useState('');
  const [itemType, setItemType] = useState('text');
  const [itemCriteria, setItemCriteria] = useState('');
  
  // 文件上传状态
  const [uploadedFiles, setUploadedFiles] = useState<UploadFile[]>([]);
  const [referenceFiles, setReferenceFiles] = useState<UploadFile[]>([]);
  const [validating, setValidating] = useState(false);
  const [validationResults, setValidationResults] = useState<any[]>([]);
  
  // 调试提示词功能状态
  const [debugRuleDescription, setDebugRuleDescription] = useState('');
  const [optimizedPrompt, setOptimizedPrompt] = useState('');
  const [optimizing, setOptimizing] = useState(false);
  // 扩展结果折叠状态
  const [expandedResults, setExpandedResults] = useState<Record<string, boolean>>({});
  // 面板状态
  const [sceneRuleCollapsed, setSceneRuleCollapsed] = useState(false);
  const [showValidationResults, setShowValidationResults] = useState(false);
  // 监听校验结果变化，控制面板显示
  useEffect(() => {
    setShowValidationResults(validationResults.length > 0);
  }, [validationResults]);

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
  
  // 初始化数据
  useEffect(() => {
    fetchScenes();
    fetchRules();
    fetchAuditItems();
  }, []);
  
  // 业务场景操作
  const showSceneModal = (scene?: BusinessScene) => {
    if (scene) {
      setEditingScene(scene);
      setSceneName(scene.name);
      setSceneDescription(scene.description || '');
    } else {
      setEditingScene(null);
      setSceneName('');
      setSceneDescription('');
    }
    setSceneModalVisible(true);
  };
  
  const handleSceneCancel = () => {
    setSceneModalVisible(false);
    setEditingScene(null);
    setSceneName('');
    setSceneDescription('');
  };
  
  const handleSceneSubmit = async (values: any) => {
    try {
      if (editingScene) {
        await axios.put(`http://localhost:8000/api/scenes/${editingScene._id}/`, values);
        message.success('更新业务场景成功');
      } else {
        await axios.post('http://localhost:8000/api/scenes/', values);
        message.success('新增业务场景成功');
      }
      
      handleSceneCancel();
      fetchScenes();
    } catch (error) {
      message.error('操作失败');
      console.error('Error submitting scene:', error);
    }
  };
  
  const handleSceneDelete = async (sceneId: string) => {
    console.log('handleSceneDelete invoked, sceneId=', sceneId);

    // Try to show Antd confirm; if for some reason it doesn't render, fallback to window.confirm
    try {
      Modal.confirm({
        title: '确认删除',
        content: '确定要删除这个业务场景吗？删除后，该场景下的所有规则也将被删除！',
        okText: '确定',
        okType: 'danger',
        cancelText: '取消',
        onOk: async () => {
          try {
            console.log('sending DELETE /api/scenes/', sceneId);
            await axios.delete(`http://localhost:8000/api/scenes/${sceneId}`);
            message.success('删除业务场景成功');
            // 如果删除的是当前选中的场景，清除选中状态，避免界面仍显示已删除的内容
            if (selectedScene === sceneId) {
              setSelectedScene('');
              setSelectedRule('');
            }

            // 刷新数据
            await fetchScenes();
            await fetchRules();
            await fetchAuditItems();
          } catch (error) {
            console.error('Error deleting scene:', error);
            const e: any = error;
            if (e?.response) {
              message.error(`删除业务场景失败: ${e.response.status} ${JSON.stringify(e.response.data)}`);
            } else if (e?.message) {
              message.error(`删除业务场景失败: ${e.message}`);
            } else {
              message.error('删除业务场景失败');
            }
          }
        },
      });

      // short timeout to detect if Antd modal actually rendered; if not, fallback to window.confirm
      setTimeout(async () => {
        const hasModal = document.querySelector('.ant-modal-root') || document.querySelector('.ant-modal-mask') || document.querySelector('.ant-modal');
        if (!hasModal) {
          console.warn('Antd Modal.confirm did not render, falling back to window.confirm');
          const ok = window.confirm('确定要删除这个业务场景吗？删除后，该场景下的所有规则也将被删除！');
          if (ok) {
            try {
              console.log('fallback: sending DELETE /api/scenes/', sceneId);
              await axios.delete(`http://localhost:8000/api/scenes/${sceneId}`);
              message.success('删除业务场景成功');
              if (selectedScene === sceneId) {
                setSelectedScene('');
                setSelectedRule('');
              }
              await fetchScenes();
              await fetchRules();
              await fetchAuditItems();
            } catch (error) {
              console.error('Error deleting scene (fallback):', error);
              const e: any = error;
              if (e?.response) {
                message.error(`删除业务场景失败: ${e.response.status} ${JSON.stringify(e.response.data)}`);
              } else if (e?.message) {
                message.error(`删除业务场景失败: ${e.message}`);
              } else {
                message.error('删除业务场景失败');
              }
            }
          }
        }
      }, 200);
    } catch (err) {
      console.error('Modal.confirm threw error, fallback to window.confirm', err);
      const ok = window.confirm('确定要删除这个业务场景吗？删除后，该场景下的所有规则也将被删除！');
      if (ok) {
        try {
          await axios.delete(`http://localhost:8000/api/scenes/${sceneId}`);
          message.success('删除业务场景成功');
          if (selectedScene === sceneId) {
            setSelectedScene('');
            setSelectedRule('');
          }
          await fetchScenes();
          await fetchRules();
          await fetchAuditItems();
        } catch (error) {
          console.error('Error deleting scene (fallback after exception):', error);
          const e: any = error;
          if (e?.response) {
            message.error(`删除业务场景失败: ${e.response.status} ${JSON.stringify(e.response.data)}`);
          } else if (e?.message) {
            message.error(`删除业务场景失败: ${e.message}`);
          } else {
            message.error('删除业务场景失败');
          }
        }
      }
    }
  };
  
  // 规则操作
  const showRuleModal = (rule?: Rule) => {
    if (rule) {
      setEditingRule(rule);
      setRuleName(rule.name);
      setRuleSceneId(rule.scene_id);
    } else {
      setEditingRule(null);
      setRuleName('');
      setRuleSceneId(selectedScene || '');
    }
    setRuleModalVisible(true);
  };
  
  const handleRuleCancel = () => {
    setRuleModalVisible(false);
    setEditingRule(null);
    setRuleName('');
    setRuleSceneId(selectedScene || '');
  };
  
  // 直接添加规则函数
  const handleAddRuleDirectly = async () => {
    try {
      const ruleData = {
        name: newRuleName.trim() || '未命名规则',
        scene_id: selectedScene,
      };
      
      await axios.post('http://localhost:8000/api/rules/', ruleData);
      message.success('新增规则成功');
      
      // 重置状态
      setNewRuleName('');
      setShowNewRuleInput(false);
      fetchRules();
    } catch (error) {
      message.error('新增规则失败');
      console.error('Error adding rule directly:', error);
    }
  };
  
  const handleRuleSubmit = async (values: any) => {
    try {
      if (editingRule) {
        await axios.put(`http://localhost:8000/api/rules/${editingRule._id}/`, values);
        message.success('更新规则成功');
      } else {
        await axios.post('http://localhost:8000/api/rules/', values);
        message.success('新增规则成功');
      }
      
      handleRuleCancel();
      fetchRules();
      fetchAuditItems();
    } catch (error) {
      message.error('操作失败');
      console.error('Error submitting rule:', error);
    }
  };
  
  const handleRuleDelete = async (ruleId: string) => {
    console.log('handleRuleDelete invoked, ruleId=', ruleId);
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个规则吗？同时会删除关联的审核项。',
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          console.log('sending DELETE /api/rules/', ruleId);
          await axios.delete(`http://localhost:8000/api/rules/${ruleId}`);
          message.success('删除规则成功');
          // 如果删除的是当前选中的规则，清除选中状态
          if (selectedRule === ruleId) {
            setSelectedRule('');
          }

          // 刷新数据
          await fetchRules();
          await fetchAuditItems();
        } catch (error) {
          console.error('Error deleting rule:', error);
          const e: any = error;
          if (e?.response) {
            message.error(`删除规则失败: ${e.response.status} ${JSON.stringify(e.response.data)}`);
          } else if (e?.message) {
            message.error(`删除规则失败: ${e.message}`);
          } else {
            message.error('删除规则失败');
          }
        }
      },
    });
  };
  
  // 审核项操作
  const showItemModal = (item?: AuditItem) => {
    if (item) {
      setEditingItem(item);
      setItemName(item.name);
      setItemRuleId(item.rule_id);
      setItemType(item.type);
      setItemCriteria(item.criteria);
    } else {
      setEditingItem(null);
      setItemName('');
      setItemRuleId(selectedRule || '');
      setItemType('text');
      setItemCriteria('');
    }
    setItemModalVisible(true);
  };
  
  const handleItemCancel = () => {
    setItemModalVisible(false);
    setEditingItem(null);
    setItemName('');
    setItemRuleId(selectedRule || '');
    setItemType('text');
    setItemCriteria('');
  };
  
  const handleItemSubmit = async (values: any) => {
    try {
      if (editingItem) {
        await axios.put(`http://localhost:8000/api/audit-items/${editingItem._id}/`, values);
        message.success('更新审核项成功');
      } else {
        await axios.post('http://localhost:8000/api/audit-items/', values);
        message.success('新增审核项成功');
      }
      
      handleItemCancel();
      fetchAuditItems();
    } catch (error) {
      message.error('操作失败');
      console.error('Error submitting audit item:', error);
    }
  };
  
  // 文件上传函数
  const uploadFile = async (file: File, fileList: UploadFile[], setFileList: React.Dispatch<React.SetStateAction<UploadFile[]>>) => {
    const newFile: UploadFile = {
      uid: `${Date.now()}-${Math.random()}`,
      name: file.name,
      status: 'uploading'
    };
    
    // 更新文件列表，显示上传中状态
    setFileList([...fileList, newFile]);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await axios.post('http://localhost:8000/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // 更新文件列表，显示上传成功状态
      setFileList(prev => prev.map(f => 
        f.uid === newFile.uid ? {
          ...f,
          status: 'done',
          response,
          url: response.data.file.file_path
        } : f
      ));
      
      message.success(`文件 ${file.name} 上传成功`);
    } catch (error) {
      // 更新文件列表，显示上传失败状态
      setFileList(prev => prev.map(f => 
        f.uid === newFile.uid ? {
          ...f,
          status: 'error'
        } : f
      ));
      
      message.error(`文件 ${file.name} 上传失败`);
      console.error('Error uploading file:', error);
    }
  };

  // 运行规则校验
  const runValidation = async () => {
    if (!selectedRule) {
      message.error('请先选择一个规则');
      return;
    }
    
    if (uploadedFiles.length === 0) {
      message.error('请先上传待审核文件');
      return;
    }
    
    setValidating(true);
    try {
      // 准备请求数据
      const requestData = {
        rule_id: selectedRule,
        files: uploadedFiles.map(file => ({
          uid: file.uid,
          name: file.name,
          url: file.response?.file?.file_path || file.url
        })),
        reference_files: referenceFiles.map((file: UploadFile) => ({
          uid: file.uid,
          name: file.name,
          url: file.response?.file?.file_path || file.url
        }))
      };
      
      // 调用后端校验API
      const response = await axios.post('http://localhost:8000/api/rules/validate', requestData);
      
      // 处理校验结果
      setValidationResults(response.data.results || []);
      message.success('规则校验完成');
    } catch (error) {
      message.error('规则校验失败');
      console.error('Error running validation:', error);
    } finally {
      setValidating(false);
    }
  };
  
  // AI优化规则描述
  const optimizeRuleDescription = async () => {
    if (!debugRuleDescription.trim()) {
      message.error('请先输入规则描述');
      return;
    }
    
    setOptimizing(true);
    try {
      // 调用后端AI优化API
      const response = await axios.post('http://localhost:8000/api/rules/optimize', {
        description: debugRuleDescription.trim()
      });
      
      // 处理优化结果
      const optimized = response.data.optimized_prompt || '';
      setOptimizedPrompt(optimized);
      
      message.success('规则描述优化完成');
    } catch (error) {
      message.error('规则描述优化失败');
      console.error('Error optimizing rule:', error);
    } finally {
      setOptimizing(false);
    }
  };

  // 切换结果展开状态
  const toggleResultExpanded = (fileName: string) => {
    setExpandedResults(prev => ({
      ...prev,
      [fileName]: !prev[fileName]
    }));
  };

  return (
    <div className="full-flow-debug" style={{ height: '100vh', overflow: 'hidden', display: 'flex', flexDirection: 'column', padding: '16px' }}>
      <h2 className="page-title" style={{ marginBottom: '16px' }}>全流程调试界面</h2>
      
      <div style={{ display: 'flex', flex: 1, gap: '16px', overflow: 'hidden' }}>
        {/* 左侧：业务场景与规则 */}
        {!sceneRuleCollapsed && (
          <div style={{ flex: 0.25, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            {/* 业务场景和规则管理 */}
            <Card 
              title="业务场景与规则" 
              bordered={false} 
              extra={
                <Button 
                  type="default" 
                  icon={<MinusOutlined />} 
                  onClick={() => setSceneRuleCollapsed(true)}
                  size="small"
                  style={{ backgroundColor: '#f0f0f0' }}
                >
                  收起目录
                </Button>
              }
              style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}
            >
              <div style={{ display: 'flex', gap: '16px', overflow: 'hidden', flex: 1 }}>
              {/* 业务场景 */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <h4 style={{ margin: 0, fontSize: '14px', fontWeight: 'bold' }}>业务场景</h4>
                  <Button 
                    type="primary" 
                    icon={<PlusOutlined />} 
                    onClick={() => showSceneModal()} 
                    size="small"
                    style={{ height: '28px', fontSize: '12px' }}
                  >
                    新建
                  </Button>
                </div>
                
                <div style={{ flex: 1, overflowY: 'auto' }}>
                  {scenes.map((scene) => (
                    <div 
                      key={scene._id}
                      onClick={() => setSelectedScene(scene._id)}
                    style={{
                      padding: '8px 12px',
                      marginBottom: '4px',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      backgroundColor: selectedScene === scene._id ? '#e6eef5' : 'transparent',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                    >
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 'bold', fontSize: '14px' }}>{scene.name}</div>
                      </div>
                      <div style={{ display: 'flex', gap: '2px' }}>
                        <Button 
                          type="text" 
                          icon={<EditOutlined />} 
                          onClick={(e) => {
                            e.stopPropagation();
                            showSceneModal(scene);
                          }} 
                          size="small"
                          style={{ padding: '0 4px', fontSize: '12px', minWidth: '24px', height: '24px', lineHeight: '24px' }}
                        />
                        <Button 
                          type="text" 
                          danger
                          icon={<DeleteOutlined />} 
                          onClick={(e) => {
                            e.stopPropagation();
                            handleSceneDelete(scene._id);
                          }} 
                          size="small"
                          style={{ padding: '0 4px', fontSize: '12px', minWidth: '24px', height: '24px', lineHeight: '24px' }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* 垂直分隔线 */}
              <div style={{ width: '1px', backgroundColor: '#f0f0f0', margin: '0 8px' }}></div>
              
              {/* 规则 */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <h4 style={{ margin: 0, fontSize: '14px', fontWeight: 'bold' }}>规则</h4>
                </div>
                
                <div style={{ flex: 1, overflowY: 'auto' }}>
                  {selectedScene ? (
                    <>
                      {/* 直接添加规则输入框 */}
                      <div style={{ marginBottom: '8px' }}>
                        {showNewRuleInput ? (
                          <div style={{ 
                            padding: '8px 12px', 
                            borderRadius: '4px', 
                            backgroundColor: '#f0f0f0',
                            display: 'flex',
                            gap: '8px',
                            alignItems: 'center'
                          }}>
                            <Input
                              placeholder="请输入规则名称"
                              value={newRuleName}
                              onChange={(e) => setNewRuleName(e.target.value)}
                              onPressEnter={handleAddRuleDirectly}
                              style={{ flex: 1, height: '32px', fontSize: '14px' }}
                            />
                            <Button 
                              type="primary" 
                              size="small"
                              onClick={handleAddRuleDirectly}
                              style={{ height: '32px', fontSize: '12px' }}
                            >
                              保存
                            </Button>
                            <Button 
                              type="default" 
                              size="small"
                              onClick={() => {
                                setShowNewRuleInput(false);
                                setNewRuleName('');
                              }}
                              style={{ height: '32px', fontSize: '12px' }}
                            >
                              取消
                            </Button>
                          </div>
                        ) : (
                          <Button 
                            type="dashed" 
                            icon={<PlusOutlined />} 
                            onClick={() => setShowNewRuleInput(true)}
                            size="small"
                            style={{ width: '100%', height: '32px', fontSize: '12px', justifyContent: 'center' }}
                          >
                            点击添加新规则
                          </Button>
                        )}
                      </div>
                      
                      {/* 规则列表 */}
                      {rules.filter(rule => rule.scene_id === selectedScene).map((rule) => (
                        <div key={rule._id} style={{ marginBottom: '8px' }}>
                          <div 
                            onClick={() => setSelectedRule(rule._id)}
                          style={{
                            padding: '8px 12px',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            backgroundColor: selectedRule === rule._id ? '#e6eef5' : 'transparent',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center'
                          }}
                          >
                            <div style={{ flex: 1 }}>
                              <div style={{ fontWeight: 'bold', fontSize: '14px' }}>{rule.name}</div>
                            </div>
                            <div style={{ display: 'flex', gap: '2px' }}>
                              <Button 
                                type="text" 
                                icon={<EditOutlined />} 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  showRuleModal(rule);
                                }} 
                                size="small"
                                style={{ padding: '0 4px', fontSize: '12px', minWidth: '24px', height: '24px', lineHeight: '24px' }}
                              />
                              <Button 
                                type="text" 
                                danger 
                                icon={<DeleteOutlined />} 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleRuleDelete(rule._id);
                                }} 
                                size="small"
                                style={{ padding: '0 4px', fontSize: '12px', minWidth: '24px', height: '24px', lineHeight: '24px' }}
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </>
                  ) : (
                    <div style={{ textAlign: 'center', color: '#999', padding: '20px 0', fontSize: '14px' }}>
                      请先选择一个业务场景
                    </div>
                  )}
                </div>
              </div>
            </div>
          </Card>
        </div>
        )}
        
        {/* 中间：规则校验 */}
        <div style={{ flex: sceneRuleCollapsed ? (showValidationResults ? 0.6 : 1) : (showValidationResults ? 0.4 : 0.75), display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <Card 
            title={
              sceneRuleCollapsed ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Button 
                    type="default" 
                    icon={<PlusOutlined />} 
                    onClick={() => setSceneRuleCollapsed(false)}
                    size="small"
                    style={{ backgroundColor: '#f0f0f0' }}
                  >
                    展开目录
                  </Button>
                  规则校验
                </div>
              ) : '规则校验'
            } 
            bordered={false} 
            style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}
          >
            <Form style={{ flex: 1, overflow: 'auto', paddingRight: '8px' }}>
              {/* AI优化工作流卡片 */}
              <Card 
                title="AI优化工作流" 
                variant="outlined"
                style={{ marginBottom: '16px', border: '1px solid #f0f0f0' }}
                extra={<div style={{ fontSize: '12px', color: '#666' }}>🔍 在此输入原始执行逻辑，AI将为您生成优化方案</div>}
              >
                <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
                  {/* 原始执行逻辑 */}
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '8px', color: '#1890ff' }}>📝 原始执行逻辑</div>
                    <Input.TextArea
                      placeholder="请输入执行逻辑，例如：结合关联文档的《巡察整改台账》的【问题描述】信息，判断《整改方案》的整改任务中具体问题是否有缺漏"
                      rows={4}
                      value={debugRuleDescription}
                      onChange={(e) => setDebugRuleDescription(e.target.value)}
                      style={{ marginBottom: '8px' }}
                      maxLength={500}
                      showCount
                    />
                  </div>
                  
                  {/* 中间操作区 */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '8px', paddingTop: '24px' }}>
                    <div style={{ width: '40px', height: '40px', borderRadius: '50%', backgroundColor: '#f0f0f0', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px' }}>
                      →
                    </div>
                    <Button
                      type="primary"
                      icon={<MessageOutlined />}
                      onClick={optimizeRuleDescription}
                      loading={optimizing}
                      disabled={!debugRuleDescription.trim()}
                      size="small"
                      style={{ minWidth: '120px' }}
                    >
                      {optimizing ? '优化中...' : '生成优化结果'}
                    </Button>
                    <div style={{ fontSize: '12px', color: '#999' }}>点击生成AI优化方案</div>
                  </div>
                  
                  {/* AI优化结果 */}
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '8px', color: '#52c41a' }}>✨ AI优化结果</div>
                    <Input.TextArea
                      placeholder={optimizing ? "AI正在优化中，请稍候..." : "AI优化后的提示词会显示在这里，您可以继续编辑"}
                      rows={4}
                      value={optimizedPrompt}
                      onChange={(e) => setOptimizedPrompt(e.target.value)}
                      maxLength={1000}
                      showCount
                      disabled={optimizing}
                    />
                    {optimizedPrompt && (
                      <div style={{ display: 'flex', gap: '8px', marginTop: '8px', justifyContent: 'flex-end' }}>
                        <Button
                          type="default"
                          size="small"
                          onClick={() => {
                            navigator.clipboard.writeText(optimizedPrompt);
                            message.success('复制成功');
                          }}
                        >
                          复制结果
                        </Button>
                        <Button
                          type="default"
                          size="small"
                          onClick={() => setOptimizedPrompt('')}
                        >
                          清空
                        </Button>
                        <Button
                          type="primary"
                          size="small"
                          onClick={() => setDebugRuleDescription(optimizedPrompt)}
                        >
                          应用优化结果
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
              
              {/* 待审核文件上传 */}
              <Form.Item label="待审核文件">
                <div style={{ border: '1px dashed #d9d9d9', borderRadius: '4px', padding: '12px', minHeight: '100px' }}>
                  {uploadedFiles.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
                      {uploadedFiles.map((file) => (
                        <div key={file.uid} style={{ padding: '6px', backgroundColor: '#f5f5f5', borderRadius: '3px', fontSize: '13px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span>{file.name}</span>
                          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                            <span style={{ color: file.status === 'done' ? '#52c41a' : '#ff4d4f', fontSize: '12px' }}>
                              {file.status === 'done' ? '已上传' : file.status === 'error' ? '上传失败' : file.status === 'uploading' ? '上传中' : ''}
                            </span>
                            {file.status === 'done' && (
                              <Button 
                                type="text" 
                                danger 
                                size="small" 
                                icon={<DeleteOutlined />} 
                                onClick={() => {
                                  setUploadedFiles(prev => prev.filter(f => f.uid !== file.uid));
                                }}
                                style={{ padding: '0', fontSize: '12px' }}
                              />
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div style={{ textAlign: 'center', color: '#999', padding: '12px 0', fontSize: '14px', marginBottom: '12px' }}>
                      点击上传待审核文件
                    </div>
                  )}
                  <Button 
                    type="primary" 
                    icon={<UploadOutlined />} 
                    onClick={() => {
                      // 触发文件选择
                      const input = document.createElement('input');
                      input.type = 'file';
                      input.multiple = true;
                      input.onchange = async (e) => {
                        const files = (e.target as HTMLInputElement).files;
                        if (files) {
                          // 遍历文件，逐个上传
                          for (let i = 0; i < files.length; i++) {
                            await uploadFile(files[i], uploadedFiles, setUploadedFiles);
                          }
                        }
                      };
                      input.click();
                    }}
                    size="small"
                  >
                    上传文件
                  </Button>
                </div>
              </Form.Item>
              
              {/* 参考材料上传 */}
              <Form.Item label="参考材料">
                <div style={{ border: '1px dashed #d9d9d9', borderRadius: '4px', padding: '12px', minHeight: '100px' }}>
                  {referenceFiles.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
                      {referenceFiles.map((file: UploadFile) => (
                        <div key={file.uid} style={{ padding: '6px', backgroundColor: '#f5f5f5', borderRadius: '3px', fontSize: '13px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span>{file.name}</span>
                          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                            <span style={{ color: file.status === 'done' ? '#52c41a' : '#ff4d4f', fontSize: '12px' }}>
                              {file.status === 'done' ? '已上传' : file.status === 'error' ? '上传失败' : file.status === 'uploading' ? '上传中' : ''}
                            </span>
                            {file.status === 'done' && (
                              <Button 
                                type="text" 
                                danger 
                                size="small" 
                                icon={<DeleteOutlined />} 
                                onClick={() => {
                                  setReferenceFiles(prev => prev.filter(f => f.uid !== file.uid));
                                }}
                                style={{ padding: '0', fontSize: '12px' }}
                              />
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div style={{ textAlign: 'center', color: '#999', padding: '12px 0', fontSize: '14px', marginBottom: '12px' }}>
                      点击上传参考材料（可选）
                    </div>
                  )}
                  <Button 
                    icon={<UploadOutlined />} 
                    onClick={() => {
                      // 触发文件选择
                      const input = document.createElement('input');
                      input.type = 'file';
                      input.multiple = true;
                      input.onchange = async (e) => {
                        const files = (e.target as HTMLInputElement).files;
                        if (files) {
                          // 遍历文件，逐个上传
                          for (let i = 0; i < files.length; i++) {
                            await uploadFile(files[i], referenceFiles, setReferenceFiles);
                          }
                        }
                      };
                      input.click();
                    }}
                    size="small"
                  >
                    上传参考材料
                  </Button>
                </div>
              </Form.Item>
              
              <Form.Item style={{ textAlign: 'center', marginTop: '20px' }}>
                <Button 
                  type="primary" 
                  icon={<PlayCircleOutlined />} 
                  onClick={runValidation}
                  loading={validating}
                  disabled={!selectedRule || uploadedFiles.length === 0}
                  size="large"
                  style={{ width: '100%', height: '40px', fontSize: '14px' }}
                >
                  开始校验
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </div>
        
        {/* 右侧：校验结果 */}
        {showValidationResults && (
          <div style={{ flex: sceneRuleCollapsed ? 0.4 : 0.35, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            {/* 校验结果 */}
            <Card title="校验结果" bordered={false} style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <div style={{ flex: 1, overflow: 'auto', paddingRight: '8px' }}>
              {validationResults.length > 0 ? (
                <>
                  {/* 结果统计 */}
                  <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: '#f0f5ff', borderRadius: '4px' }}>
                    <div style={{ display: 'flex', gap: '24px', fontSize: '14px' }}>
                      <div>
                        <span style={{ fontWeight: 'bold', marginRight: '8px' }}>总文件数：</span>
                        <span>{validationResults.length}</span>
                      </div>
                      <div>
                        <span style={{ fontWeight: 'bold', marginRight: '8px' }}>通过：</span>
                        <span style={{ color: '#52c41a', fontWeight: 'bold' }}>
                          {validationResults.filter(item => item.result === '通过').length}
                        </span>
                      </div>
                      <div>
                        <span style={{ fontWeight: 'bold', marginRight: '8px' }}>不通过：</span>
                        <span style={{ color: '#ff4d4f', fontWeight: 'bold' }}>
                          {validationResults.filter(item => item.result === '不通过').length}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {/* 结果列表 */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {validationResults.map((item, index) => (
                      <Card 
                        key={index} 
                        title={item.fileName} 
                        bordered={false} 
                        extra={
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ 
                              fontSize: '14px', 
                              fontWeight: 'bold',
                              color: item.result === '通过' ? '#52c41a' : '#ff4d4f'
                            }}>
                              {item.result}
                            </span>
                            {item.result === '通过' ? 
                              <CheckCircleOutlined style={{ color: '#52c41a', fontSize: '18px' }} /> : 
                              <DeleteOutlined style={{ color: '#ff4d4f', fontSize: '18px' }} />
                            }
                          </div>
                        }
                        style={{ boxShadow: '0 2px 8px rgba(0, 0, 0, 0.09)' }}
                        actions={[
                          <Button 
                            type="text" 
                            onClick={() => toggleResultExpanded(item.fileName)}
                            size="small"
                          >
                            {expandedResults[item.fileName] ? '收起详情' : '查看详情'}
                          </Button>
                        ]}
                      >
                        <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>规则：{item.ruleName}</div>
                        
                        {/* 详细理由 - 可折叠 */}
                        {expandedResults[item.fileName] && (
                          <div style={{ marginTop: '12px', padding: '12px', backgroundColor: '#fafafa', borderRadius: '4px' }}>
                            <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '8px' }}>审核理由：</div>
                            {Array.isArray(item.reason) ? (
                              <ul style={{ margin: 0, paddingLeft: '20px' }}>
                                {item.reason.map((reason: string, idx: number) => (
                                  <li key={idx} style={{ fontSize: '14px', marginBottom: '4px', color: '#333' }}>{reason}</li>
                                ))}
                              </ul>
                            ) : (
                              <div style={{ fontSize: '14px', color: '#333' }}>{item.reason}</div>
                            )}
                          </div>
                        )}
                      </Card>
                    ))}
                  </div>
                </>
              ) : (
                <div style={{ textAlign: 'center', padding: '40px 0', color: '#999', fontSize: '14px' }}>
                  暂无校验结果，请先上传文件并点击"开始校验"
                </div>
              )}
            </div>
          </Card>
        </div>
        )}
      </div>
      
      {/* 业务场景模态框 */}
      <Modal
        title={editingScene ? '编辑业务场景' : '新建业务场景'}
        open={sceneModalVisible}
        onCancel={handleSceneCancel}
        width={500}
        maskClosable={false}
        destroyOnClose
        style={{ top: 100 }}
        styles={{ body: { maxHeight: '70vh', overflowY: 'auto' } }}
        footer={[
          <Button key="cancel" onClick={handleSceneCancel}>
            取消
          </Button>,
          <Button key="submit" type="primary" onClick={() => {
            if (!sceneName.trim()) {
              message.error('请输入场景名称');
              return;
            }
            handleSceneSubmit({
              name: sceneName.trim(),
              description: sceneDescription.trim()
            });
          }}>
            确定
          </Button>
        ]}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>场景名称</label>
            <Input 
              placeholder="请输入场景名称" 
              value={sceneName} 
              onChange={(e) => setSceneName(e.target.value)} 
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>场景描述</label>
            <Input.TextArea 
              placeholder="请输入场景描述" 
              rows={4} 
              value={sceneDescription} 
              onChange={(e) => setSceneDescription(e.target.value)} 
            />
          </div>
        </div>
      </Modal>
      
      {/* 规则模态框 */}
      <Modal
        title={editingRule ? '编辑规则' : '新建规则'}
        open={ruleModalVisible}
        onCancel={handleRuleCancel}
        footer={[
          <Button key="cancel" onClick={handleRuleCancel}>
            取消
          </Button>,
          <Button key="submit" type="primary" onClick={() => {
            if (!ruleName.trim()) {
              message.error('请输入规则名称');
              return;
            }
            if (!ruleSceneId.trim()) {
              message.error('请选择所属业务场景');
              return;
            }
            handleRuleSubmit({
              name: ruleName.trim(),
              scene_id: ruleSceneId.trim()
            });
          }}>
            确定
          </Button>
        ]}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>规则名称</label>
            <Input 
              placeholder="请输入规则名称" 
              value={ruleName} 
              onChange={(e) => setRuleName(e.target.value)} 
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>所属业务场景</label>
            <Select 
              placeholder="请选择业务场景" 
              value={ruleSceneId} 
              onChange={(value) => setRuleSceneId(value)} 
              style={{ width: '100%' }}
            >
              {scenes.map(scene => (
                <Select.Option key={scene._id} value={scene._id}>{scene.name}</Select.Option>
              ))}
            </Select>
          </div>
        </div>
      </Modal>
      
      {/* 审核项模态框 */}
      <Modal
        title={editingItem ? '编辑审核项' : '新建审核项'}
        open={itemModalVisible}
        onCancel={handleItemCancel}
        footer={[
          <Button key="cancel" onClick={handleItemCancel}>
            取消
          </Button>,
          <Button key="submit" type="primary" onClick={() => {
            if (!itemName.trim()) {
              message.error('请输入审核项名称');
              return;
            }
            if (!itemRuleId.trim()) {
              message.error('请选择所属规则');
              return;
            }
            handleItemSubmit({
              name: itemName.trim(),
              rule_id: itemRuleId.trim(),
              type: itemType,
              criteria: itemCriteria.trim()
            });
          }}>
            确定
          </Button>
        ]}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>审核项名称</label>
            <Input 
              placeholder="请输入审核项名称" 
              value={itemName} 
              onChange={(e) => setItemName(e.target.value)} 
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>所属规则</label>
            <Select 
              placeholder="请选择所属规则" 
              value={itemRuleId} 
              onChange={(value) => setItemRuleId(value)} 
              style={{ width: '100%' }}
            >
              {rules.filter(rule => rule.scene_id === selectedScene).map(rule => (
                <Select.Option key={rule._id} value={rule._id}>{rule.name}</Select.Option>
              ))}
            </Select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>审核项类型</label>
            <Select 
              placeholder="请选择审核项类型" 
              value={itemType} 
              onChange={(value) => setItemType(value)} 
              style={{ width: '100%' }}
            >
              <Select.Option value="text">文本</Select.Option>
              <Select.Option value="number">数字</Select.Option>
              <Select.Option value="date">日期</Select.Option>
              <Select.Option value="boolean">布尔值</Select.Option>
            </Select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>审核标准</label>
            <Input.TextArea 
              placeholder="请输入审核标准" 
              rows={4} 
              value={itemCriteria} 
              onChange={(e) => setItemCriteria(e.target.value)} 
            />
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default FullFlowDebug;