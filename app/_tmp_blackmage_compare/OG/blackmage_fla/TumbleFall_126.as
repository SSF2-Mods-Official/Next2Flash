package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class TumbleFall_126 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var self:BlackMageExt;

        public function TumbleFall_126()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }


    }
}

