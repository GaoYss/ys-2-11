import { CalendarPlus, Eye, Plus, X } from "lucide-react";
import { useState } from "react";
import { SectionHeader } from "../../components/SectionHeader";

const DEFAULT_TIME_SLOTS = ["09:00-11:00", "14:00-16:00", "19:00-21:00"];

function getDefaultStartDate() {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return tomorrow.toISOString().split("T")[0];
}

export function ScheduleBoard({
  classes,
  courses,
  schedule,
  suspendedDates,
  onGenerate,
  onPreview,
  onAddSuspendedDate,
  onDeleteSuspendedDate,
}) {
  const [classId, setClassId] = useState("");
  const [startDate, setStartDate] = useState(getDefaultStartDate());
  const [days, setDays] = useState(8);
  const [selectedTimeSlots, setSelectedTimeSlots] = useState(
    DEFAULT_TIME_SLOTS.reduce((acc, slot) => ({ ...acc, [slot]: true }), {})
  );
  const [previewData, setPreviewData] = useState(null);
  const [suspendedDate, setSuspendedDate] = useState("");
  const [suspendedReason, setSuspendedReason] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  const activeTimeSlots = Object.entries(selectedTimeSlots)
    .filter(([, selected]) => selected)
    .map(([slot]) => slot);

  function toggleTimeSlot(slot) {
    setSelectedTimeSlots((prev) => ({
      ...prev,
      [slot]: !prev[slot],
    }));
  }

  async function handlePreview(event) {
    event.preventDefault();
    if (activeTimeSlots.length === 0) {
      alert("请至少选择一个时段");
      return;
    }
    setIsGenerating(true);
    try {
      const result = await onPreview({
        class_id: classId || undefined,
        start_date: startDate,
        days,
        time_slots: activeTimeSlots,
      });
      setPreviewData(result);
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleGenerate(event) {
    event.preventDefault();
    if (activeTimeSlots.length === 0) {
      alert("请至少选择一个时段");
      return;
    }
    setIsGenerating(true);
    try {
      await onGenerate({
        class_id: classId || undefined,
        start_date: startDate,
        days,
        time_slots: activeTimeSlots,
      });
      setPreviewData(null);
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleAddSuspended(event) {
    event.preventDefault();
    if (!suspendedDate) {
      alert("请选择日期");
      return;
    }
    await onAddSuspendedDate({
      date: suspendedDate,
      reason: suspendedReason,
    });
    setSuspendedDate("");
    setSuspendedReason("");
  }

  const displaySessions = previewData ? previewData.sessions : schedule;
  const displaySkipped = previewData ? previewData.skipped : [];

  return (
    <section className="module">
      <form className="toolbar-panel" onSubmit={handleGenerate}>
        <label>
          排课班级
          <select value={classId} onChange={(event) => setClassId(event.target.value)}>
            <option value="">全部班级</option>
            {classes.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          起始日期
          <input
            type="date"
            value={startDate}
            onChange={(event) => setStartDate(event.target.value)}
          />
        </label>
        <label>
          生成课次数
          <input
            min="1"
            max="60"
            type="number"
            value={days}
            onChange={(event) => setDays(Number(event.target.value))}
          />
        </label>
        <div className="time-slots-group">
          <span className="time-slots-label">可用时段</span>
          <div className="time-slots-options">
            {DEFAULT_TIME_SLOTS.map((slot) => (
              <label key={slot} className="time-slot-option">
                <input
                  type="checkbox"
                  checked={selectedTimeSlots[slot]}
                  onChange={() => toggleTimeSlot(slot)}
                />
                {slot}
              </label>
            ))}
          </div>
        </div>
        <button
          className="secondary-action"
          type="button"
          onClick={handlePreview}
          disabled={isGenerating}
        >
          <Eye size={18} />
          预览
        </button>
        <button
          className="primary-action"
          type="submit"
          disabled={isGenerating}
        >
          <CalendarPlus size={18} />
          自动生成课程表
        </button>
      </form>

      {previewData && (
        <div className="notice info">
          <strong>预览模式</strong>：当前显示的是预览结果，点击"自动生成课程表"按钮确认保存。
        </div>
      )}

      {displaySkipped.length > 0 && (
        <div className="table-panel">
          <SectionHeader eyebrow="Skipped" title="跳过日期" />
          <div className="skipped-list">
            {displaySkipped.map((item, index) => (
              <div key={index} className="skipped-item">
            <span className="skipped-date">{item.date}</span>
            <span className="skipped-reason">{item.reason}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="table-panel">
        <SectionHeader eyebrow="Schedule" title={previewData ? "预览课程表" : "课程表"} />
        <div className="schedule-grid">
          {displaySessions.map((session) => (
            <article className="schedule-card" key={session.id}>
              <span>{session.date}</span>
              <h3>{session.course_title}</h3>
              <p>{session.class_name}</p>
              <div>
                <small>{session.time}</small>
                <small>{session.room}</small>
                <small>{session.teacher}</small>
              </div>
            </article>
          ))}
        </div>
      </div>

      <div className="table-panel">
        <SectionHeader eyebrow="Suspended" title="停课日期管理" />
        <form className="suspended-form" onSubmit={handleAddSuspended}>
          <label>
            日期
            <input
              type="date"
              value={suspendedDate}
              onChange={(event) => setSuspendedDate(event.target.value)}
            />
          </label>
          <label>
            原因
            <input
              type="text"
              placeholder="如：节假日、活动等"
              value={suspendedReason}
              onChange={(event) => setSuspendedReason(event.target.value)}
            />
          </label>
          <button className="primary-action" type="submit">
            <Plus size={18} />
            添加停课
          </button>
        </form>
        {suspendedDates.length > 0 && (
          <div className="suspended-list">
            {suspendedDates.map((item) => (
              <div key={item.id} className="suspended-item">
                <span>{item.date}</span>
                <span>{item.reason || "停课"}</span>
                <button
                  type="button"
                  className="icon-button"
                  onClick={() => onDeleteSuspendedDate(item.date)}
                >
                  <X size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="table-panel">
        <SectionHeader eyebrow="Courses" title="课程库" />
        <div className="course-tags">
          {courses.map((course) => (
            <span key={course.id}>
              {course.title} · {course.duration}课时 · {course.category}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
