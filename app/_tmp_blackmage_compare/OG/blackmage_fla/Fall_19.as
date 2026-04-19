package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Fall_19 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function Fall_19()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }

        internal function frame6():*
        {
            this.self.stancePlayFrame("redo");
        }


    }
}

