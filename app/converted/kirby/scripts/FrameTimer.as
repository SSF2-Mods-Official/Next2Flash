package
{
    public class FrameTimer
    {

        private var m_duration:int;
        private var m_elapsedFrames:int;
        private var m_data:Object;

        public function FrameTimer(_arg_1:int):void
        {
            m_duration = _arg_1;
            m_elapsedFrames = 0;
            m_data = null;
        }

        public function get data():Object
        {
            return m_data;
        }

        public function set data(_arg_1:Object):void
        {
            m_data = _arg_1;
        }

        public function get completed():Boolean
        {
            return m_elapsedFrames >= m_duration;
        }

        public function get duration():int
        {
            return m_duration;
        }

        public function set duration(_arg_1:int):void
        {
            if ((_arg_1 < 0))
            {
                m_duration = 0;
            }
            else
            {
                m_duration = _arg_1;
                if ((m_elapsedFrames > m_duration))
                {
                    m_elapsedFrames = m_duration;
                };
            };
        }

        public function get elapsedFrames():int
        {
            return m_elapsedFrames;
        }

        public function set elapsedFrames(_arg_1:int):void
        {
            if ((_arg_1 < 0))
            {
                m_elapsedFrames = 0;
            }
            else
            {
                m_elapsedFrames = ((_arg_1 > m_duration) ? m_duration : _arg_1);
            };
        }

        public function tick(_arg_1:int=1):void
        {
            elapsedFrames = (m_elapsedFrames + _arg_1);
        }

        public function finish():void
        {
            m_elapsedFrames = m_duration;
        }

        public function reset():void
        {
            m_elapsedFrames = 0;
        }


    }
}

