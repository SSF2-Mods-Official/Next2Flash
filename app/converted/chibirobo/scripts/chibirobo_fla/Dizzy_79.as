package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class Dizzy_79 extends MovieClip
    {

        public var dizzy_stars:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function Dizzy_79()
        {
            super();
            addFrameScript(0, this.frame1, 16, this.frame17);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
        }

        internal function frame17():*
        {
            this.gotoAndStop("loop");
        }


    }
}

