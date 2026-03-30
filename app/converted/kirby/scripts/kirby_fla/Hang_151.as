package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Hang_151 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function Hang_151()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 20, this.frame21, 29, this.frame30);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("kirbyPeachUsed", false);
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

        internal function frame21():*
        {
            gotoAndStop("loop");
        }

        internal function frame30():*
        {
            this.gotoAndStop("hang");
        }


    }
}

