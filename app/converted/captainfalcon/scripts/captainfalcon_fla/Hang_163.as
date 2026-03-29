package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Hang_163 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;

        public function Hang_163()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 16, this.frame17);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
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

        internal function frame17():*
        {
            this.gotoAndStop("loop");
        }


    }
}

