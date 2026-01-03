import ReactMarkdown from 'react-markdown';
import './WebContent.css';

// Process content to style inline citations like [1], [2], etc.
const formatCitations = (text) => {
    if (typeof text !== 'string') return text;

    // Replace [1], [2], etc. with styled citation spans
    return text.replace(/\[(\d+)\]/g, '<cite class="citation">[$1]</cite>');
};

const WebContent = ({ content, isLoading }) => {
    if (!content && !isLoading) {
        return (
            <div className="web-content-empty">
                <div className="empty-icon">📚</div>
                <h3>No Web Content Available</h3>
                <p>Content is being generated or not available for this subtopic.</p>
            </div>
        );
    }

    // Show loading skeleton if loading
    if (isLoading && !content) {
        return (
            <div className="web-content">
                <article className="web-article">
                    <div className="loading-skeleton">
                        <div className="skeleton-line title"></div>
                        <div className="skeleton-line"></div>
                        <div className="skeleton-line"></div>
                        <div className="skeleton-line short"></div>
                        <div className="skeleton-line"></div>
                        <div className="skeleton-line"></div>
                    </div>
                </article>
            </div>
        );
    }

    // Check if content has a Sources section
    const hasSourcesSection = content && (
        content.includes('## Sources') ||
        content.includes('### Sources') ||
        content.includes('## References') ||
        content.includes('### References')
    );

    return (
        <div className="web-content">
            <article className={`web-article ${hasSourcesSection ? 'has-sources' : ''}`}>
                <ReactMarkdown
                    components={{
                        // Custom styling for markdown elements
                        h1: ({ children }) => <h1 className="md-h1">{children}</h1>,
                        h2: ({ children }) => {
                            const text = children?.toString() || '';
                            const isSourcesHeader = text.toLowerCase().includes('sources') || text.toLowerCase().includes('references');
                            return <h2 className={`md-h2 ${isSourcesHeader ? 'sources-header' : ''}`}>{children}</h2>;
                        },
                        h3: ({ children }) => {
                            const text = children?.toString() || '';
                            const isSourcesHeader = text.toLowerCase().includes('sources') || text.toLowerCase().includes('references');
                            return <h3 className={`md-h3 ${isSourcesHeader ? 'sources-header' : ''}`}>{children}</h3>;
                        },
                        h4: ({ children }) => <h4 className="md-h4">{children}</h4>,
                        p: ({ children }) => (
                            <p
                                className="md-paragraph"
                                dangerouslySetInnerHTML={{
                                    __html: formatCitations(
                                        typeof children === 'string' ? children :
                                            Array.isArray(children) ? children.map(c => typeof c === 'string' ? c : '').join('') : ''
                                    ) || ''
                                }}
                            />
                        ),
                        ul: ({ children }) => <ul className="md-list">{children}</ul>,
                        ol: ({ children }) => <ol className="md-list ordered">{children}</ol>,
                        li: ({ children }) => <li className="md-list-item">{children}</li>,
                        strong: ({ children }) => <strong className="md-bold">{children}</strong>,
                        em: ({ children }) => <em className="md-italic">{children}</em>,
                        blockquote: ({ children }) => <blockquote className="md-quote">{children}</blockquote>,
                        code: ({ inline, children }) =>
                            inline
                                ? <code className="md-inline-code">{children}</code>
                                : <pre className="md-code-block"><code>{children}</code></pre>,
                        a: ({ href, children }) => (
                            <a href={href} target="_blank" rel="noopener noreferrer" className="md-link">
                                {children}
                            </a>
                        ),
                    }}
                >
                    {content}
                </ReactMarkdown>
                {isLoading && (
                    <div className="streaming-indicator">
                        <span className="dot"></span>
                        <span className="dot"></span>
                        <span className="dot"></span>
                    </div>
                )}
            </article>
        </div>
    );
};

export default WebContent;
