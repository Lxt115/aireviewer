// 调试按钮点击事件的脚本
// 可以在浏览器控制台中运行

console.log('=== 调试按钮点击事件 ===');

// 查找所有按钮
const buttons = document.querySelectorAll('.ant-btn-primary');
console.log('找到的主要按钮数量:', buttons.length);

buttons.forEach((button, index) => {
  console.log(`\n按钮 ${index + 1}:`);
  console.log('文本:', button.textContent.trim());
  console.log('类名:', button.className);
  console.log('位置:', button.getBoundingClientRect());
  
  // 检查是否有元素覆盖按钮
  const rect = button.getBoundingClientRect();
  const elementsUnderButton = document.elementsFromPoint(
    rect.left + rect.width / 2,
    rect.top + rect.height / 2
  );
  
  console.log('按钮上方的元素:', elementsUnderButton.map(el => el.tagName));
  
  // 检查事件监听器
  if (typeof getEventListeners === 'function') {
    console.log('事件监听器:', getEventListeners(button));
  }
});

// 特别检查确认按钮
const confirmButtons = document.querySelectorAll('[type="button"]:contains("确 定")');
console.log('\n=== 确认按钮 ===');
console.log('找到的确认按钮数量:', confirmButtons.length);

confirmButtons.forEach((button, index) => {
  console.log(`\n确认按钮 ${index + 1}:`);
  console.log('HTML:', button.outerHTML);
  console.log('是否可见:', button.offsetWidth > 0 && button.offsetHeight > 0);
  
  // 添加调试点击事件
  button.addEventListener('click', (e) => {
    console.log('确认按钮被点击!');
    console.log('事件对象:', e);
    console.log('事件是否被取消:', e.defaultPrevented);
    
    // 阻止冒泡以查看是否是冒泡问题
    e.stopPropagation();
  }, true); // 使用捕获阶段
});

console.log('=== 调试完成 ===');