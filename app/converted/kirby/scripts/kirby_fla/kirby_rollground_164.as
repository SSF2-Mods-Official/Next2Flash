package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class kirby_rollground_164 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function kirby_rollground_164()
        {
            super();
            addFrameScript(0, this.frame1, 12, this.frame13, 17, this.frame18);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame13():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }


    }
}

