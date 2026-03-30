package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_crouch_74 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_crouch_74()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 5, this.frame6);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame4():*
        {
            this.self.setGlobalVariable("crouchdown", true);
        }

        internal function frame6():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

