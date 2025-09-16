import React, { useState, useMemo } from "react";

const SearchMediaCards = ({ mainData = [], itemsPerPage = 12 }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [hoveredCard, setHoveredCard] = useState(null);

  // 计算分页数据
  const { paginatedData, totalPages } = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginated = mainData.slice(startIndex, endIndex);
    const total = Math.ceil(mainData.length / itemsPerPage);

    return {
      paginatedData: paginated,
      totalPages: total,
    };
  }, [mainData, currentPage, itemsPerPage]);

  // 分页控制
  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
      // 滚动到顶部
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  // 生成页码数组
  const getPageNumbers = () => {
    const pages = [];
    const maxVisible = 5;

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      const start = Math.max(1, currentPage - 2);
      const end = Math.min(totalPages, start + maxVisible - 1);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
    }

    return pages;
  };

  // 卡片组件
  const MediaCard = ({ item, index }) => {
    const isHovered = hoveredCard === `${currentPage}-${index}`;
    const [titleHovered, setTitleHovered] = useState(false);

    const handleCardClick = () => {
      // 跳转到详情页面
      window.location.href = `/details?vod_id=${item.vod_id}`;
    };

    return (
      <div
        className={`
          relative bg-white rounded-2xl overflow-hidden shadow-lg border border-gray-100
          transform transition-all duration-300 ease-out cursor-pointer
          ${
            isHovered
              ? "scale-105 shadow-2xl -translate-y-2 border-red-200"
              : "hover:shadow-xl"
          }
        `}
        onMouseEnter={() => setHoveredCard(`${currentPage}-${index}`)}
        onMouseLeave={() => setHoveredCard(null)}
        onClick={handleCardClick}
      >
        {/* 海报图片 */}
        <div className="relative aspect-[3/4] overflow-hidden bg-gray-100">
          <img
            src={item.vod_pic || "/api/placeholder/300/400"}
            alt={item.vod_name}
            className={`
              w-full h-full object-cover transition-transform duration-500
              ${isHovered ? "scale-110" : "scale-100"}
            `}
            onError={(e) => {
              e.target.src = "/api/placeholder/300/400";
            }}
          />

          {/* 悬停时的遮罩层 */}
          <div
            className={`
            absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent
            transition-opacity duration-300
            ${isHovered ? "opacity-100" : "opacity-0"}
          `}
          >
            <div className="absolute bottom-4 left-4 right-4 text-white">
              <div className="flex items-center justify-center">
                <div className="flex items-center space-x-2 bg-black/50 rounded-full px-4 py-2 backdrop-blur-sm">
                  <span className="text-sm font-medium">查看详情</span>
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          {/* 更新标签 */}
          {item.vod_remarks && (
            <div className="absolute top-3 left-3">
              <span
                className={`
                px-3 py-1 text-xs font-bold rounded-full
                ${
                  item.vod_remarks.includes("全")
                    ? "bg-green-500 text-white"
                    : "bg-orange-500 text-white"
                }
                shadow-lg
              `}
              >
                {item.vod_remarks}
              </span>
            </div>
          )}
        </div>

        {/* 卡片内容 */}
        <div className="p-4">
          {/* 标题 - 添加tooltip显示完整标题 */}
          <div className="relative mb-3">
            <h3
              className="font-bold text-gray-900 text-base leading-tight truncate cursor-pointer"
              title={item.vod_name}
              onMouseEnter={() => setTitleHovered(true)}
              onMouseLeave={() => setTitleHovered(false)}
            >
              {item.vod_name}
            </h3>

            {/* Tooltip显示完整标题 */}
            {titleHovered && item.vod_name.length > 12 && (
              <div className="absolute z-50 bottom-full left-0 right-0 mb-2 p-2 bg-gray-800 text-white text-sm rounded-lg shadow-lg break-words">
                {item.vod_name}
                <div className="absolute top-full left-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-gray-800"></div>
              </div>
            )}
          </div>

          {/* 分类标签 */}
          {item.vod_class && (
            <div className="flex items-center">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                {item.vod_class}
              </span>
            </div>
          )}
        </div>
      </div>
    );
  };

  // 分页组件
  const Pagination = () => {
    if (totalPages <= 1) return null;

    return (
      <div className="flex items-center justify-center mt-12 space-x-2">
        {/* 上一页按钮 */}
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className={`
            px-4 py-2 rounded-lg font-medium transition-all duration-200
            ${
              currentPage === 1
                ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 hover:border-red-300"
            }
          `}
        >
          上一页
        </button>

        {/* 页码按钮 */}
        {getPageNumbers().map((page) => (
          <button
            key={page}
            onClick={() => handlePageChange(page)}
            className={`
              px-4 py-2 rounded-lg font-medium transition-all duration-200
              ${
                page === currentPage
                  ? "bg-red-500 text-white shadow-lg"
                  : "bg-white text-gray-700 border border-gray-300 hover:bg-red-50 hover:border-red-300"
              }
            `}
          >
            {page}
          </button>
        ))}

        {/* 下一页按钮 */}
        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className={`
            px-4 py-2 rounded-lg font-medium transition-all duration-200
            ${
              currentPage === totalPages
                ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 hover:border-red-300"
            }
          `}
        >
          下一页
        </button>
      </div>
    );
  };

  if (!mainData || mainData.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 text-lg mb-4">
          <svg
            className="w-16 h-16 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 110 2h-1v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6H3a1 1 0 110-2h4zM9 6v11a1 1 0 102 0V6a1 1 0 10-2 0zm4 0v11a1 1 0 102 0V6a1 1 0 10-2 0z"
            />
          </svg>
          暂无数据
        </div>
        <p className="text-gray-500">请尝试搜索您感兴趣的影视作品</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* 结果统计 */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-2xl font-bold text-gray-900">搜索结果</h2>
          <span className="text-gray-500 font-medium">
            共找到 {mainData.length} 个结果
          </span>
        </div>
        <div className="text-sm text-gray-500">
          第 {currentPage} 页，共 {totalPages} 页
        </div>
      </div>

      {/* 卡片网格 */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-6">
        {paginatedData.map((item, index) => (
          <MediaCard
            key={`${item.vod_id}-${currentPage}-${index}`}
            item={item}
            index={index}
          />
        ))}
      </div>

      {/* 分页组件 */}
      <Pagination />
    </div>
  );
};

export default SearchMediaCards;
