import { useState } from "react";

const MediaDetails = ({ vodDetails }) => {
  // 获取所有来源的键名作为tab标签
  const sources = Object.keys(vodDetails.list);
  const [activeSource, setActiveSource] = useState(sources[0]);

  // 处理剧集数据，按数字排序
  const getEpisodeList = (sourceData) => {
    return Object.entries(sourceData)
      .map(([episode, url]) => ({ episode: parseInt(episode), url }))
      .sort((a, b) => a.episode - b.episode);
  };

  const currentEpisodes = getEpisodeList(vodDetails.list[activeSource]);

  return (
    <div className="w-full bg-white">
      {/* 主要内容区域 */}
      <div className="flex flex-col lg:flex-row gap-6 p-6">
        {/* 左侧海报 */}
        <div className="flex-shrink-0">
          <img
            src={vodDetails.vod_pic}
            alt={vodDetails.vod_name}
            className="w-80 h-auto object-cover rounded-lg shadow-lg"
          />
        </div>

        {/* 右侧信息 */}
        <div className="flex-1 space-y-6">
          {/* 标题 */}
          <h1 className="text-3xl font-bold text-gray-900">
            {vodDetails.vod_name}
          </h1>

          {/* 信息列表 */}
          <div className="space-y-3 text-base">
            <div className="flex items-start">
              <span className="text-gray-600 w-16 flex-shrink-0">类型：</span>
              <span className="text-red-600">{vodDetails.vod_class}</span>
            </div>

            <div className="flex items-start">
              <span className="text-gray-600 w-16 flex-shrink-0">标签：</span>
              <span className="text-gray-800">{vodDetails.vod_tag}</span>
            </div>

            <div className="flex items-start">
              <span className="text-gray-600 w-16 flex-shrink-0">演员：</span>
              <span className="text-gray-800 leading-relaxed">
                {vodDetails.vod_actor}
              </span>
            </div>

            <div className="flex items-start">
              <span className="text-gray-600 w-16 flex-shrink-0">导演：</span>
              <span className="text-gray-800">{vodDetails.vod_director}</span>
            </div>

            <div className="flex items-start">
              <span className="text-gray-600 w-16 flex-shrink-0">发布：</span>
              <span className="text-gray-800">{vodDetails.vod_pubdate}</span>
            </div>
          </div>

          {/* 剧情简介 */}
          <div className="bg-gray-50 p-4 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              剧情简介
            </h3>
            <div className="text-gray-700 leading-relaxed">
              {vodDetails.vod_description}
            </div>
          </div>
        </div>
      </div>

      {/* 剧集列表 */}
      <div className="px-6 pb-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-1 h-6 bg-red-500 rounded"></div>
          <h3 className="text-lg font-semibold text-gray-900">剧集列表</h3>
        </div>

        {/* Tab容器 */}
        <div className="w-full">
          {/* Tab按钮 */}
          <div className="flex border-b border-gray-200 mb-4">
            {sources.map((source) => (
              <button
                key={source}
                onClick={() => setActiveSource(source)}
                className={`px-4 py-2 font-medium text-sm transition-colors relative ${
                  activeSource === source
                    ? "text-red-600 border-b-2 border-red-600"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                {source}
              </button>
            ))}
          </div>

          {/* Tab内容 */}
          <div className="grid grid-cols-8 sm:grid-cols-12 md:grid-cols-16 lg:grid-cols-20 gap-3">
            {currentEpisodes.map(({ episode, url }) => (
              <a
                key={episode}
                href={`/preview?url=${encodeURIComponent(url)}&douban_id=${
                  vodDetails.vod_douban_id
                }&episode_number=${episode}`}
                className="aspect-square bg-white border border-gray-300 rounded-lg flex items-center justify-center text-sm font-medium text-gray-700 hover:bg-red-50 hover:border-red-400 hover:text-red-600 transition-all duration-200 shadow-sm hover:shadow-md"
              >
                {episode}
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MediaDetails;
