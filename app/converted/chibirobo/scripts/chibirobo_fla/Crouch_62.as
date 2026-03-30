package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class Crouch_62 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var xframe:String;

        public function Crouch_62()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 4, this.frame5);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            this.xframe = null;
            if (parent && SSF2API.isReady())
            {
                this.self.setGlobalVariable("tether", false);
            };
        }

        internal function frame2():*
        {
            this.self.playSound("chibi_Bend");
        }

        internal function frame4():*
        {
            this.self.setGlobalVariable("crouchdown", true);
        }

        internal function frame5():*
        {
            gotoAndStop("loop");
        }


    }
}

