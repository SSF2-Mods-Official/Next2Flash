// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.ItemHeavyShoot_94

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemHeavyShoot_94 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function ItemHeavyShoot_94()
        {
            addFrameScript(0, this.frame1, 3, this.frame4, 25, this.frame26);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }

        internal function frame4():*
        {
            this.self.getItem().activateItem();
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-7),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame26():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

