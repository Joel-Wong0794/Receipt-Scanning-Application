import { BrowserRouter, Routes, Route } from "react-router-dom";
import CapturePage from "./pages/CapturePage.jsx";
import ReviewPage from "./pages/ReviewPage.jsx";
import HistoryPage from "./pages/HistoryPage.jsx";
import DetailPage from "./pages/DetailPage.jsx";
import SuccessPage from "./pages/SuccessPage.jsx";
import BottomNav from "./components/BottomNav.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<CapturePage />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="/success" element={<SuccessPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/receipts/:id" element={<DetailPage />} />
        </Routes>
        <BottomNav />
      </div>
    </BrowserRouter>
  );
}
