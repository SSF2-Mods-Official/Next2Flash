package
{
    public dynamic class GameAndWatchApple extends SSF2Item
    {

        public function GameAndWatchApple(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function initialize():void
        {
            setFrameInterrupt(this.handleInterrupt);
        }

        override public function update():void
        {
        }

        public function handleInterrupt(_arg_1:Object):Boolean
        {
            var _local_2:* = _arg_1.character;
            SSF2API.playSound("eat_heart");
            _local_2.recover(8);
            attachEffect("global_sparkle");
            destroy();
            return true;
        }


    }
}

