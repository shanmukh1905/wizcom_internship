import React, { useState, useEffect } from "react";

const EditTrigger = ({ trigger, isOpen, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    SYMBOL: "",
    SERIES: "",
    HNI: "",
    LOP: "",
    BOP: "",
    DEVIATION: "",
    COMMENTS: "",
    STATUS: "ACTIVE",
  });

  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if (trigger) {
      setFormData({
        SYMBOL: trigger.SYMBOL,
        SERIES: trigger.SERIES,
        HNI: trigger.HNI,
        LOP: trigger.LOP,
        BOP: trigger.BOP,
        DEVIATION: trigger.DEVIATION,
        COMMENTS: trigger.COMMENTS,
        STATUS: trigger.STATUS,
      });
    }
  }, [trigger]);

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const validateForm = () => {
    if (!formData.SYMBOL.trim() || !formData.SERIES.trim() || !formData.STATUS) {
      return "Please fill in all required fields.";
    }
    if (formData.LOP && isNaN(parseFloat(formData.LOP))) {
      return "LOP must be a valid number.";
    }
    if (formData.BOP && isNaN(parseFloat(formData.BOP))) {
      return "BOP must be a valid number.";
    }
    if (formData.DEVIATION && isNaN(parseFloat(formData.DEVIATION))) {
      return "Deviation must be a valid number.";
    }
    return "";
  };

  const handleSubmit = () => {
    const error = validateForm();
    if (error) {
      setErrorMessage(error);
      return;
    }
    setErrorMessage("");
    onSave(formData);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Escape") onClose();
  };

  if (!isOpen) return null;

  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-labelledby="modal-title"
      aria-describedby="modal-description"
      onKeyDown={handleKeyDown}
      tabIndex="-1"
    >
      <div className="modal-content">
        <h3 id="modal-title">Edit Trigger</h3>
        <form id="modal-description">
          {errorMessage && <p className="error-message">{errorMessage}</p>}
          <div>
            <label>Symbol:</label>
            <input
              type="text"
              name="SYMBOL"
              value={formData.SYMBOL || ""}
              onChange={handleFormChange}
              placeholder="Enter Symbol"
              required
              disabled
            />
          </div>
          <div>
            <label>Series:</label>
            <input
              type="text"
              name="SERIES"
              value={formData.SERIES || ""}
              onChange={handleFormChange}
              placeholder="Enter Series"
              required
              disabled
            />
          </div>
          <div>
            <label>HNI:</label>
            <input
              type="text"
              name="HNI"
              value={formData.HNI || ""}
              onChange={handleFormChange}
              placeholder="Enter HNI (optional)"
            />
          </div>
          <div>
            <label>LOP:</label>
            <input
              type="number"
              name="LOP"
              value={formData.LOP || ""}
              onChange={handleFormChange}
              placeholder="Enter LOP (optional)"
            />
          </div>
          <div>
            <label>BOP:</label>
            <input
              type="number"
              name="BOP"
              value={formData.BOP || ""}
              onChange={handleFormChange}
              placeholder="Enter BOP (optional)"
            />
          </div>
          <div>
            <label>Deviation:</label>
            <input
              type="number"
              name="DEVIATION"
              value={formData.DEVIATION || ""}
              onChange={handleFormChange}
              placeholder="Enter Deviation"
              required
            />
          </div>
          <div>
            <label>Comments:</label>
            <input
              type="text"
              name="COMMENTS"
              value={formData.COMMENTS || ""}
              onChange={handleFormChange}
              placeholder="Enter Comments (optional)"
            />
          </div>
          <div>
            <label>Status:</label>
            <select
              name="STATUS"
              value={formData.STATUS || "ACTIVE"}
              onChange={handleFormChange}
            >
              <option value="ACTIVE">Active</option>
              <option value="INACTIVE">Inactive</option>
            </select>
          </div>
          <button type="button" onClick={handleSubmit}>
            Save
          </button>
          <button type="button" onClick={onClose}>
            Cancel
          </button>
        </form>
      </div>
    </div>
  );
};

export default EditTrigger;
