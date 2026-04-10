import { useState } from "react";
import FeedbackModal from "./FeedbackModal";

export default function FeedbackButton() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button className="btn btn-sm" onClick={() => setOpen(true)}>Feedback</button>
      {open && <FeedbackModal onClose={() => setOpen(false)} />}
    </>
  );
}

