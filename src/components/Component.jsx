function Component({ component }) {
  return (
    <div className="component">
      <div className="component-content">
        {/* 现有的组件内容... */}
      </div>
      {component.note?.trim() && (
        <div className="component-note" title={component.note}>
          <span className="note-icon">📝</span>
          {component.note}
        </div>
      )}
    </div>
  );
}

export default Component; 