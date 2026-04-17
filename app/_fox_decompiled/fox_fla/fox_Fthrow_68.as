package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_Fthrow_68 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:FoxExt;

        public function fox_Fthrow_68()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 10, this.frame11, 17, this.frame18);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
        }

        internal function frame2():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame11():*
        {
            this.self.playVoiceSound(1);
            SSF2API.getCamera().shake(9);
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }


    }
}

