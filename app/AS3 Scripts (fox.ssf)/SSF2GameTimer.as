// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2GameTimer

package 
{
    import flash.display.MovieClip;

    public class SSF2GameTimer extends SSF2BaseAPIObject 
    {

        public function SSF2GameTimer(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function getType():String
        {
            return ("SSF2GameTimer");
        }

        public function getCurrentTime():int
        {
            return (_api.getCurrentTime());
        }

        public function setCurrentTime(_arg_1:int):void
        {
            _api.setCurrentTime(_arg_1);
        }

        public function start():void
        {
            _api.start();
        }

        public function restart():void
        {
            _api.restart();
        }

        public function stop():void
        {
            _api.stop();
        }

        public function getMC():MovieClip
        {
            return (_api.getMC());
        }

        public function setEndGameOptions(_arg_1:Object):void
        {
            _api.setEndGameOptions(_arg_1);
        }


    }
}//package 

