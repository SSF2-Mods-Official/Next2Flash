// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2CustomMenu

package 
{
    import flash.display.MovieClip;

    public class SSF2CustomMenu extends SSF2BaseAPIObject 
    {

        public function SSF2CustomMenu(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function getType():String
        {
            return ("SSF2CustomMenu");
        }

        public function getMC():MovieClip
        {
            return (_api.getMC());
        }

        public function show():void
        {
            _api.show();
        }

        public function remove():void
        {
            _api.remove();
        }

        public function setCustomInputMapping(_arg_1:Object):void
        {
            _api.setCustomInputMapping(_arg_1);
        }


    }
}//package 

