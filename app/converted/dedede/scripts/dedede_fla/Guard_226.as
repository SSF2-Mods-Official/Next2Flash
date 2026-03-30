package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Guard_226 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function Guard_226()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 9, this.frame10);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
        }

        internal function frame4():*
        {
            gotoAndStop("loop");
        }

        internal function frame10():*
        {
            this.self.endAttack();
        }


    }
}

