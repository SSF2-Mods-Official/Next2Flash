package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class LedgeHang_222 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function LedgeHang_222()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 31, this.frame32);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
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

        internal function frame32():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

