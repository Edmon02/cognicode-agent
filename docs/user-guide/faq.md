# ❓ Frequently Asked Questions

> Common questions and answers about CogniCode Agent

## 🎯 General Questions

### What is CogniCode Agent?
CogniCode Agent is an AI-powered development tool that provides real-time code analysis, intelligent refactoring suggestions, and automated unit test generation. It's designed to improve code quality and developer productivity.

### Is CogniCode Agent free to use?
Yes, CogniCode Agent is open-source and free to use under the MIT license. You can use it for both personal and commercial projects.

### What makes CogniCode Agent different from other code analysis tools?
- **Privacy-first**: All AI processing runs locally on your machine
- **Multi-agent architecture**: Specialized AI agents for different tasks
- **Real-time analysis**: Instant feedback as you type
- **Comprehensive features**: Analysis, refactoring, and test generation in one tool
- **Modern UI**: Beautiful, responsive interface

## 🔧 Installation & Setup

### What are the system requirements?
- **RAM**: 4GB minimum, 8GB+ recommended
- **Storage**: 5GB+ free space for AI models
- **OS**: macOS, Linux, or Windows 10+
- **Node.js**: Version 16.0+
- **Python**: Version 3.8+

### Why is the initial setup taking so long?
The first setup downloads AI models (2-5GB total) which can take time depending on your internet connection. Subsequent starts are much faster as models are cached locally.

### I'm getting "port already in use" errors. How do I fix this?
```bash
# Kill processes using the default ports
sudo lsof -ti:3000 | xargs kill -9  # Frontend port
sudo lsof -ti:5000 | xargs kill -9  # Backend port

# Or specify different ports
PORT=3001 npm run dev              # Frontend
cd server && PORT=5001 python app.py  # Backend
```

### The setup script failed. How can I install manually?
Follow the [Manual Installation Guide](installation.md#-manual-installation) which provides step-by-step instructions for manual setup.

## 🤖 AI Models & Analysis

### How accurate are the AI analysis results?
- **Bug detection**: ~90% accuracy for common issues
- **Performance suggestions**: ~85% relevance rate
- **Test generation**: ~80% functional test coverage
- **Refactoring suggestions**: ~95% compilation success rate

Accuracy varies by programming language and code complexity.

### Which programming languages are supported?
**Tier 1 (Full Support)**: JavaScript, TypeScript, Python, Java, C++
**Tier 2 (Core Features)**: C#, Go, Rust, PHP, Ruby
**Tier 3 (Basic Support)**: Kotlin, Swift, Scala, R, Shell Scripts

See the [Features Overview](features.md#multi-language-support) for details.

### Can I use CogniCode Agent with my existing IDE?
Currently, CogniCode Agent runs as a standalone web application. IDE integration is planned for future releases. You can copy code between your IDE and CogniCode Agent.

### How long does analysis take?
- **Quick analysis**: 10-30 seconds
- **Standard analysis**: 30-90 seconds  
- **Deep analysis**: 1-3 minutes

Time varies based on code size and system performance.

## 🔒 Privacy & Security

### Is my code sent to external servers?
No! All AI processing happens locally on your machine. Your code never leaves your computer, ensuring complete privacy.

### What data does CogniCode Agent collect?
CogniCode Agent doesn't collect any user data, analytics, or telemetry. It's completely privacy-first.

### Can I use CogniCode Agent offline?
Yes, once the AI models are downloaded, CogniCode Agent works completely offline.

### Is it safe to analyze proprietary/confidential code?
Yes, since all processing is local and no data is transmitted, it's safe to analyze any code including proprietary and confidential projects.

## ⚡ Performance & Optimization

### CogniCode Agent is running slowly. How can I improve performance?
1. **Increase RAM**: 8GB+ recommended for optimal performance
2. **Close other applications**: Free up system resources
3. **Use SSD storage**: Faster model loading
4. **Analyze smaller code chunks**: Break large files into functions
5. **Use Quick analysis**: For faster results

### The AI models are using too much disk space. Can I reduce this?
You can remove unused models:
```bash
cd server/models
# Remove specific language models you don't use
rm -rf codebert-java/  # If you don't use Java
```

Minimum space requirement is ~1GB for core models.

### Can I run CogniCode Agent on a low-end machine?
Yes, but with limitations:
- Use Quick analysis mode
- Analyze smaller code snippets
- Close other applications
- Consider using demo mode (lighter models)

## 🎨 User Interface

### How do I change the editor theme?
The editor supports multiple themes. Use the theme selector in the header or modify the theme in settings.

### Can I increase the font size in the editor?
Yes, use standard browser zoom (Ctrl/Cmd + +) or configure Monaco editor settings.

### The results panel is too small. How can I resize it?
Drag the panel divider to resize. The layout is responsive and remembers your preferences.

### Can I export analysis results?
Yes, use the Export button to download results in various formats:
- JSON (structured data)
- PDF (formatted report)
- Markdown (documentation)

## 🔄 Code Analysis

### Why aren't issues being detected in my code?
1. **Check language selection**: Ensure the correct language is selected
2. **Verify syntax**: Fix any syntax errors first
3. **Use complete functions**: Partial code may not analyze well
4. **Try different analysis depth**: Use Standard or Deep analysis
5. **Check file size**: Very large files may timeout

### The refactoring suggestions seem wrong. Why?
- AI suggestions are recommendations, not requirements
- Context matters - the AI may not understand your specific requirements
- Some suggestions prioritize different goals (performance vs readability)
- Always review suggestions before applying

### How do I improve test generation quality?
1. **Provide complete functions**: Include full function signatures
2. **Add comments**: Describe expected behavior
3. **Include example usage**: Show how the function should be called
4. **Specify edge cases**: Comment on special conditions

## 🚀 Advanced Usage

### Can I customize the analysis rules?
Currently, rules are built into the AI models. Custom rule configuration is planned for future releases.

### How do I integrate CogniCode Agent into my CI/CD pipeline?
Use the REST API to integrate with your build process:
```bash
# Example CI script
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "'$(cat src/main.js)'", "language": "javascript"}'
```

### Can I run multiple analyses simultaneously?
Yes, the backend supports concurrent requests. The frontend queues analyses automatically.

### How do I update CogniCode Agent?
```bash
git pull origin main
npm install                    # Update frontend dependencies
cd server && pip install -r requirements.txt  # Update backend
```

## 🐛 Troubleshooting

### The application won't start. What should I check?
1. **Verify prerequisites**: Node.js, Python, and all dependencies
2. **Check ports**: Ensure 3000 and 5000 are available
3. **Review logs**: Check console for error messages
4. **Restart services**: Kill all processes and restart
5. **Clear cache**: Remove node_modules and reinstall

### I'm getting WebSocket connection errors.
1. **Check backend status**: Ensure Flask server is running
2. **Verify CORS settings**: Check backend CORS configuration
3. **Test locally**: Ensure you're accessing localhost
4. **Check firewall**: Ensure ports aren't blocked

### Analysis results are inconsistent.
This can happen due to:
- **Model randomness**: AI models have some inherent variability
- **Code context**: Small changes can affect analysis
- **Cache behavior**: Clear cache if results seem stale

### The frontend shows "Backend not connected".
1. **Verify backend is running**: Check http://localhost:5000/api/health
2. **Check network**: Ensure no proxy/firewall blocking
3. **Restart both services**: Full restart often resolves connection issues

## 🆘 Getting Help

### Where can I report bugs?
- **GitHub Issues**: [Create a new issue](https://github.com/Edmon02/cognicode-agent/issues)
- **Include details**: Error messages, steps to reproduce, system info

### How do I request new features?
- **GitHub Discussions**: [Start a discussion](https://github.com/Edmon02/cognicode-agent/discussions)
- **Feature requests**: Use the feature request template

### Where can I get community support?
- **GitHub Discussions**: Community Q&A and tips
- **Discord** (coming soon): Real-time chat support
- **Documentation**: Comprehensive guides and tutorials

### How do I contribute to the project?
See the [Contributing Guide](../developer-guide/contributing.md) for detailed instructions on:
- Code contributions
- Documentation improvements
- Bug reports
- Feature suggestions

---

<div align="center">

**❓ Still have questions?**

[🐛 Report an Issue](https://github.com/Edmon02/cognicode-agent/issues) | [💬 Join Discussions](https://github.com/Edmon02/cognicode-agent/discussions) | [🏠 Back to Docs](../README.md)

</div>
