package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Hang_74 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function Hang_74()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 39, this.frame40, 43, this.frame44, 44, this.frame45);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (this.self && SSF2API.isReady() && this.self.getGlobalVariable("tether"))
            {
                this.self.setGlobalVariable("tether", false);
                this.self.stancePlayFrame("tether");
            };
        }

        internal function frame2():*
        {
            this.self.attachEffect("ledgeGrab_gfx", {
                "x":this.self.flipX(0),
                "y":0,
                "scaleX":-0.4,
                "scaleY":-0.4
            });
        }

        internal function frame40():*
        {
            gotoAndStop("loop");
        }

        internal function frame44():*
        {
            this.self.attachEffect("ledgeGrab_gfx", {
                "x":this.self.flipX(0),
                "y":0,
                "scaleX":-0.4,
                "scaleY":-0.4
            });
        }

        internal function frame45():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

