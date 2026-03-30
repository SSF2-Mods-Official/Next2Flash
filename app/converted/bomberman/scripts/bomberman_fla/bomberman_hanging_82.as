package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_hanging_82 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_hanging_82()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 11, this.frame12);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
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

        internal function frame12():*
        {
            this.gotoAndStop("loop");
        }


    }
}

