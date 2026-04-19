// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.ItemTilt_83

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemTilt_83 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function ItemTilt_83()
        {
            addFrameScript(0, this.frame1, 6, this.frame7, 8, this.frame9, 18, this.frame19);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }

        internal function frame7():*
        {
            this.self.getItem().activateItem();
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-7),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame9():*
        {
            this.self.getItem().deactivateItem();
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

