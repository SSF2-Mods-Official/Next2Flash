package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Fall_39 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function Fall_39()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.stancePlayFrame("back");
            };
        }

        internal function frame8():*
        {
            this.self.stancePlayFrame("back");
        }


    }
}

