package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class LedgeHang_71 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function LedgeHang_71()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 9, this.frame10);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (parent && SSF2API.isReady() && this.self)
            {
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

        internal function frame10():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

