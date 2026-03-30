package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Hang_95 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function Hang_95()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 9, this.frame10);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
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
            this.gotoAndStop("loop");
        }


    }
}

