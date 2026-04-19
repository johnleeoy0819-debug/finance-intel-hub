import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import type { GraphData } from '../api/client'

interface Props {
  data: GraphData
  width?: number
  height?: number
  onNodeClick?: (id: number) => void
}

const SENTIMENT_COLORS: Record<string, string> = {
  positive: '#22c55e',
  negative: '#ef4444',
  neutral: '#6b7280',
}

const RELATION_COLORS: Record<string, string> = {
  theme: '#94a3b8',
  cause: '#f59e0b',
  compare: '#3b82f6',
  continuation: '#8b5cf6',
}

export default function KnowledgeGraph({ data, width = 640, height = 400, onNodeClick }: Props) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!ref.current || !data.nodes.length) return

    const svg = d3.select(ref.current)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', [0, 0, width, height])

    // Arrow marker for directed edges
    svg.append('defs').append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 22)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#94a3b8')

    const nodes = data.nodes.map(n => ({ ...n }))
    const links = data.links.map(l => ({ ...l }))

    const simulation = d3.forceSimulation(nodes as any)
      .force('link', d3.forceLink(links as any).id((d: any) => d.id).distance(80))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide().radius(20))

    const link = svg.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', (d: any) => RELATION_COLORS[d.type] || '#cbd5e1')
      .attr('stroke-width', (d: any) => Math.max(1, (d.strength || 0.5) * 3))
      .attr('stroke-opacity', 0.7)
      .attr('marker-end', 'url(#arrow)')

    const node = svg.append('g')
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', (d: any) => d.id === data.center_id ? 10 : 6)
      .attr('fill', (d: any) => SENTIMENT_COLORS[d.sentiment || 'neutral'] || '#6b7280')
      .attr('stroke', (d: any) => d.id === data.center_id ? '#1f2937' : '#fff')
      .attr('stroke-width', (d: any) => d.id === data.center_id ? 3 : 1.5)
      .style('cursor', 'pointer')

    const drag = d3.drag<any, any>()
      .on('start', (event: any, d: any) => {
        if (!event.active) simulation.alphaTarget(0.3).restart()
        d.fx = d.x; d.fy = d.y
      })
      .on('drag', (event: any, d: any) => {
        d.fx = event.x; d.fy = event.y
      })
      .on('end', (event: any, d: any) => {
        if (!event.active) simulation.alphaTarget(0)
        d.fx = null; d.fy = null
      })

    node.call(drag as any)

    const label = svg.append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .text((d: any) => d.title?.slice(0, 12) || String(d.id))
      .attr('font-size', 10)
      .attr('fill', '#374151')
      .attr('dx', 10)
      .attr('dy', 3)
      .style('pointer-events', 'none')

    node.on('click', (_event: any, d: any) => {
      onNodeClick?.(d.id)
    })

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y)

      label
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y)
    })

    return () => {
      simulation.stop()
      svg.remove()
    }
  }, [data, width, height, onNodeClick])

  if (!data.nodes.length) {
    return <div className="text-center text-gray-400 py-10">暂无知识图谱数据</div>
  }

  return <div ref={ref} className="flex justify-center" />
}
