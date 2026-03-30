package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Guard_155 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function Guard_155()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 9, this.frame10);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
        }

        internal function frame4():*
        {
            gotoAndStop("again");
        }

        internal function frame10():*
        {
            this.self.endAttack();
        }


    }
}

