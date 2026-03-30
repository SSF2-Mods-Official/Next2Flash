package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemShoot_104 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function ItemShoot_104()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 15, this.frame16);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
        }

        internal function frame4():*
        {
            this.self.getItem().activateItem();
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-7)});
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}

