import React, { useEffect } from 'react';

function ComponentEdit({ component, onUpdate }) {
  const handleNoteChange = (e) => {
    const newNote = e.target.value;
    // 保存到本地存储
    localStorage.setItem(`component-note-${component.id}`, newNote);
    
    onUpdate({
      ...component,
      note: newNote
    });
  };

  // 组件加载时从本地存储获取备注
  useEffect(() => {
    const savedNote = localStorage.getItem(`component-note-${component.id}`);
    if (savedNote && !component.note) {
      onUpdate({
        ...component,
        note: savedNote
      });
    }
  }, [component.id]);

  const clearNote = () => {
    onUpdate({
      ...component,
      note: ''
    });
  };

  return (
    <div className="component-edit">
      <div className="note-section">
        <span>对自己说点什么：</span>
        <div className="note-input-wrapper">
          <input
            type="text"
            value={component.note || ''}
            onChange={handleNoteChange}
            placeholder="添加备注..."
            className="note-input"
          />
          {component.note && (
            <button 
              className="clear-note-btn"
              onClick={clearNote}
              title="清除备注"
            >
              ×
            </button>
          )}
        </div>
      </div>
      {/* 其他现有的编辑内容... */}
    </div>
  );
}

export default ComponentEdit; 