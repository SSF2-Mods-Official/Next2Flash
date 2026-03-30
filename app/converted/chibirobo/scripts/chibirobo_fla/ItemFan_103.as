package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemFan_103 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function ItemFan_103()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 5, this.frame6);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
        }

        internal function frame3():*
        {
            this.self.getItem().activateItem();
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-7)});
        }

        internal function frame4():*
        {
            this.self.getItem().deactivateItem();
        }

        internal function frame6():*
        {
            this.self.endAttack();
        }


    }
}

