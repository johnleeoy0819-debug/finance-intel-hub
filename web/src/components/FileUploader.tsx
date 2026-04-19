import { useCallback } from 'react'
import { Upload } from 'lucide-react'

interface Props {
  onUpload: (files: FileList) => void
}

export default function FileUploader({ onUpload }: Props) {
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      if (e.dataTransfer.files) onUpload(e.dataTransfer.files)
    },
    [onUpload]
  )

  return (
    <div
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-500 transition-colors"
    >
      <Upload className="w-10 h-10 mx-auto text-gray-400 mb-3" />
      <p className="text-gray-600">拖拽文件到此处 或 点击选择</p>
      <p className="text-gray-400 text-sm mt-1">支持：PDF / Word / TXT / EPUB / MP3 / MP4 / WAV / M4A</p>
      <input
        type="file"
        multiple
        className="hidden"
        onChange={(e) => e.target.files && onUpload(e.target.files)}
        id="file-input"
      />
      <label
        htmlFor="file-input"
        className="inline-block mt-3 px-4 py-2 bg-primary-600 text-white rounded-lg cursor-pointer hover:bg-primary-700"
      >
        选择文件
      </label>
    </div>
  )
}
