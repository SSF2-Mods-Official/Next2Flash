package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Skid_16 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function Skid_16()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
        }

        internal function frame6():*
        {
            this.self.endAttack();
        }


    }
}

